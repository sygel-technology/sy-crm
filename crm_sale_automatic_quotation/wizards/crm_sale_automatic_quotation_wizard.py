# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class CrmSaleAutomaticQuotationWizard(models.TransientModel):
    _name = "crm.sale.automatic.quotation.wizard"

    skip_quoted_leads = fields.Boolean(
        default=True,
    )
    force_user_id = fields.Boolean(
        string="Force User",
        default=False,
        help="If false quotations will be created with the lead user."
        " If true, quotations will be created with the chosed user",
    )
    user_id = fields.Many2one(
        string="Commercial",
        comodel_name="res.users",
        default=lambda self: self.env.user,
        required=True,
        help="User that will send the email and have the quotation assigned",
    )
    send_mail = fields.Boolean(
        default=True,
    )
    email_template = fields.Many2one(
        comodel_name="mail.template",
        domain=lambda self: [
            ("model_id", "=", self.env.ref("sale.model_sale_order").id)
        ],
        default=lambda self: self.env.ref(
            (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "crm_sale_automatic_quotation.crm_sale_automatic_quotation_wizard_email"
                )
                or "sale.email_template_edi_sale"
            ),
            False,
        ),
    )
    update_quotation_state = fields.Boolean(
        string="Update Quotations State",
        default=True,
        help="Move quotations to sent state if email sent",
    )
    update_lead_stage = fields.Boolean(
        string="Update Leads Stage",
        default=True,
        help="Move leads to configured stage in Settings/Stages",
    )
    create_activity = fields.Boolean(
        string="Create Review Activity",
        help="Create Review Activity in Leads",
        default=True,
    )
    activity_type_id = fields.Many2one(
        string="Activity Type",
        comodel_name="mail.activity.type",
        domain="['|', ('res_model', 'in', ['crm.lead']), ('res_model', '=', False)]",
        default=lambda self: self.env.ref(
            "crm_sale_automatic_quotation.review_activity", False
        ),
    )
    failed_lead_line_ids = fields.One2many(
        string="Failed Leads",
        comodel_name="crm.sale.automatic.quotation.wizard.line",
        inverse_name="wizard_id",
    )
    wizard_state = fields.Selection(
        string="field_name",
        selection=[("init", "Init"), ("review", "Review"), ("end", "End")],
        default="init",
    )

    def _create_failed_lead_lines(self, lead_ids, error):
        return self.env["crm.sale.automatic.quotation.wizard.line"].create(
            [
                {"wizard_id": self.id, "lead_id": lead.id, "error": error}
                for lead in lead_ids
            ]
        )

    def _get_error_types(self):
        # Filter Function, # Condition, # Error MSG
        return [
            (lambda li: not li.partner_id, True, _("The lead does not have a partner")),
            (
                lambda li: not li.partner_id.email,
                self.send_mail,
                _("The partner does not have an email"),
            ),
            (
                lambda li: li.order_ids.filtered(lambda o: o.state != "cancel"),
                self.skip_quoted_leads,
                _("The lead already has quotations"),
            ),
            (
                lambda li: li.type in ["lead", False],
                True,
                _("The lead is in lead state"),
            ),
        ]

    def _filter_leads_and_classify_errors(self, lead_ids):
        """
        Returns two recordsets
        - Filtered leads (crm.lead)
        - Failed leads and error reason (crm.sale.automatic.quotation.wizard.line)
        """
        filtered_leads_res = lead_ids
        invalid_leads_res = self.env["crm.sale.automatic.quotation.wizard.line"]

        error_data = self._get_error_types()
        for func, cond, error_msg in error_data:
            if cond:
                tmp_invalid_leads = filtered_leads_res.filtered(func)
                invalid_leads_res += self._create_failed_lead_lines(
                    tmp_invalid_leads, error_msg
                )
                filtered_leads_res -= tmp_invalid_leads

        return (filtered_leads_res, invalid_leads_res)

    def _send_mail(self, template, quote_ids):
        for quote in quote_ids:
            template.with_user(
                self.user_id if self.force_user_id else quote.user_id
            ).send_mail(quote.id)
            if self.update_quotation_state:
                quote.state = "sent"

    def _get_activity_deadline(self, activity_type):
        """Replicates the _calculate_date_deadline logic from v15 in v18"""
        base = fields.Date.context_today(self)
        if (
            activity_type.delay_from == "previous_activity"
            and "activity_previous_deadline" in self.env.context
        ):
            base = fields.Date.from_string(
                self.env.context.get("activity_previous_deadline")
            )
        if activity_type.delay_unit and activity_type.delay_count:
            base += relativedelta(
                **{activity_type.delay_unit: activity_type.delay_count}
            )
        return base

    def _create_activities(self, records):
        activity_model = self.env["mail.activity"]
        for rec in records:
            activity_model.create(
                {
                    "user_id": self.user_id.id
                    if self.force_user_id
                    else rec.user_id.id,
                    "res_id": rec.id,
                    "res_model_id": self.env.ref("crm.model_crm_lead").id,
                    "activity_type_id": self.activity_type_id.id,
                    "date_deadline": self._get_activity_deadline(self.activity_type_id),
                }
            )

    def _update_lead_stages(self, lead_ids):
        for lead_id in lead_ids:
            stage_id = self.env["crm.stage"]._get_crm_automatic_wizard_dest_stage(
                lead_id.team_id
            )
            if stage_id and stage_id.sequence > lead_id.stage_id.sequence:
                lead_id.stage_id = stage_id

    def _create_quotations(self, lead_ids):
        failed_lead_line_ids = self.env["crm.sale.automatic.quotation.wizard.line"]
        sucessfull_lead_ids = self.env["crm.lead"]
        created_quote_ids = self.env["sale.order"]
        for rec in lead_ids:
            try:
                quote_id = rec._action_generate_automatic_quotation(from_wizard=True)
                quote_id.user_id = self.user_id if self.force_user_id else rec.user_id
                created_quote_ids += quote_id
            except ValidationError as e:
                failed_lead_line_ids += self._create_failed_lead_lines(rec, str(e))
            else:
                sucessfull_lead_ids += rec
        if self.send_mail and self.email_template:
            self._send_mail(self.email_template, created_quote_ids)
        if self.create_activity:
            self._create_activities(sucessfull_lead_ids)
        if self.update_lead_stage:
            self._update_lead_stages(sucessfull_lead_ids)
        return failed_lead_line_ids

    def action_accept(self):
        self.ensure_one()
        if self.wizard_state == "init":
            lead_ids = self.env["crm.lead"].browse(self.env.context.get("active_ids"))
        elif self.wizard_state == "review":
            lead_ids = self.mapped("failed_lead_line_ids.lead_id")

        (correct_leads, failed_lead_line_ids) = self._filter_leads_and_classify_errors(
            lead_ids
        )
        failed_lead_line_ids += self._create_quotations(correct_leads)

        self.failed_lead_line_ids = failed_lead_line_ids
        self.wizard_state = "review" if failed_lead_line_ids else "end"
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "target": "new",
        }


class CrmSaleAutomaticQuotationWizardLine(models.TransientModel):
    _name = "crm.sale.automatic.quotation.wizard.line"

    wizard_id = fields.Many2one(
        string="Wizard",
        comodel_name="crm.sale.automatic.quotation.wizard",
        readonly=True,
    )
    lead_id = fields.Many2one(
        string="Lead",
        comodel_name="crm.lead",
    )
    error = fields.Char(
        readonly=True,
    )
