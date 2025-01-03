# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

from odoo.addons.mail.tools.parser import parse_res_ids


def _reopen(self, res_id, model, context=None):
    # save original model in context, because selecting the list of available
    # templates requires a model in context
    context = dict(context or {}, default_model=model)
    return {
        "type": "ir.actions.act_window",
        "view_mode": "form",
        "view_type": "form",
        "res_id": res_id,
        "res_model": self._name,
        "target": "new",
        "context": context,
    }


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    check_add_sale_attachments = fields.Boolean(
        string="Check sale attachments", compute="_compute_check_add_sale_attachments"
    )

    @api.depends("model", "res_ids")
    def _compute_check_add_sale_attachments(self):
        for sel in self:
            orders_ids = ()
            lead_ids = parse_res_ids(self.env.context.get("active_ids"))
            if sel.model == "crm.lead" and lead_ids and len(lead_ids) == 1:
                orders_ids = (
                    self.env[self.model]
                    .browse(lead_ids)
                    .order_ids.filtered(lambda x: x.state in ("draft", "sent"))
                )
            sel.check_add_sale_attachments = any(orders_ids)

    def calculate_sale_attachments(self):
        self.ensure_one()
        template_id = self.env.ref("sale.email_template_edi_sale")
        lead_ids = parse_res_ids(self.env.context.get("active_ids"))
        lead_objs = self.env[self.model].browse(lead_ids)
        sale_ids = lead_objs.order_ids.filtered(lambda x: x.state in ("draft", "sent"))
        if sale_ids:
            rendered_values = template_id._generate_template(
                sale_ids.ids,
                (
                    "attachment_ids",
                    "report_template_ids",
                ),
            )
            attachment_ids = []
            for r_value in rendered_values.values():
                if rendered_values.get("attachment_ids"):
                    attachment_ids += rendered_values.get("attachment_ids")
                # transform attachments into attachment_ids; not attached to the
                # document because this will be done further in the posting
                # process, allowing to clean database if email not send
                if r_value.get("attachments"):
                    attachment_ids += (
                        self.env["ir.attachment"]
                        .create(
                            [
                                {
                                    "name": attach_fname,
                                    "datas": attach_datas,
                                    "res_model": "mail.compose.message",
                                    "res_id": 0,
                                    "type": "binary",
                                }
                                for attach_fname, attach_datas in r_value.pop(
                                    "attachments"
                                )
                            ]
                        )
                        .ids
                    )
            if attachment_ids:
                self.write({"attachment_ids": [(4, id) for id in attachment_ids]})
            sale_ids.filtered(lambda x: x.state == "draft").action_quotation_sent()
        return _reopen(self, self.id, self.model, context=self._context)
