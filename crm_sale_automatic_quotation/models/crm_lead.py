# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _get_crm_automatic_quotation_values(self, quotation_template):
        self.ensure_one()
        values = {
            "opportunity_id": self.id,
            "partner_id": self.partner_id.id,
            "campaign_id": self.campaign_id.id,
            "medium_id": self.medium_id.id,
            "origin": self.name,
            "source_id": self.source_id.id,
            "company_id": self.company_id.id or self.env.company.id,
            "tag_ids": [(6, 0, self.tag_ids.ids)],
            "sale_order_template_id": quotation_template.id,
        }
        return values

    def _recompute_quotation_lines(self, order_line):
        """
        Inherit to modify the fields of the automatic quotations lines.
        """
        return order_line

    def _action_generate_automatic_quotation(self, from_wizard=False):
        self.ensure_one()
        res = self.env["sale.order"]
        template_domain = [("crm_automatic_quotation", "=", True)]
        if from_wizard:
            template_domain += [("cr_automatic_exclude_from_wizard", "=", False)]
        for template in self.env["sale.order.template"].search(template_domain):
            vals_list = []
            domain = template.crm_automatic_domain
            if domain:
                domain = expression.AND([safe_eval(domain), [("id", "=", self.id)]])
            if not domain or self.env["crm.lead"].search(domain, limit=1):
                vals_list = self._get_crm_automatic_quotation_values(template)
            if vals_list:
                quotation_id = res.create(vals_list)
                # To update the quotation template fields in the quotation
                quotation_id.with_context(
                    **dict(self._context, is_crm_automatic_quotation=True)
                )._onchange_sale_order_template_id()
                self._recompute_quotation_lines(quotation_id.order_line)
                res |= quotation_id
        if not res and not self.env.context.get("skip_no_template_err", False):
            raise ValidationError(
                _(
                    "There are no quotation templates for this opportunity. "
                    "Set up a quotation template and try again. "
                    "If you already have quotation templates, check its domain"
                )
            )
        return res

    def action_generate_automatic_quotation(self, from_wizard=False):
        self._action_generate_automatic_quotation(from_wizard)
        return self.action_view_sale_quotation()

    def action_open_crm_sale_automatic_quotation_wizard(self):
        result_view = self.env.ref(
            "crm_sale_automatic_quotation.crm_sale_automatic_quotation_wizard_form",
            raise_if_not_found=False,
        )
        ctx = {
            "active_ids": self.ids,
        }
        return {
            "name": _("Create automatic quotations"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "crm.sale.automatic.quotation.wizard",
            "views": [(result_view.id, "form")],
            "view_id": result_view.id,
            "target": "new",
            "context": ctx,
        }
