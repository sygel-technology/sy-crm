# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmSaleAutomaticQuotationWizard(models.TransientModel):
    _name = "crm.sale.automatic.quotation.wizard"

    skip_quoted_leads = fields.Boolean(
        string='Skip Quoted Leads',
        default=True,
    )
    send_mail = fields.Boolean(
        string='Send Mail',
        default=True,
    )
    email_template = fields.Many2one(
        string='Email Template',
        comodel_name='mail.template',
        domain=lambda self: [('model_id', '=', self.env.ref('sale.model_sale_order').id)],
        default=lambda self: self.env.ref(
            (self.env['ir.config_parameter'].sudo().get_param('crm_sale_automatic_quotation.crm_sale_automatic_quotation_wizard_email')
                or'sale.email_template_edi_sale'),
            False),
    )
    failed_lead_line_ids = fields.One2many(
        string='Failed Leads',
        comodel_name='crm.sale.automatic.quotation.wizard.line', 
        inverse_name='wizard_id',
    )
    wizard_state = fields.Selection(
        string='field_name',
        selection=[
            ('init', 'Init'),
            ('review', 'Review'),
            ('end', 'End')
        ],
        default='init',
    )

    def _create_failed_lead_lines(self, lead_ids, error):
        return self.env['crm.sale.automatic.quotation.wizard.line'].create([{
                'wizard_id': self.id,
                'lead_id': lead.id,
                'error': error
            } for lead in lead_ids
    ])

    def _get_error_types(self):
        # Filter Function, # Condition, # Error MSG
        return [
            (lambda l: not l.partner_id, True, _("The lead does not have a partner")),
            (lambda l: not l.partner_id.email, self.send_mail, _("The partner does not have an email")),
            (
                lambda l: l.order_ids.filtered(lambda o: o.state != "cancel" ),
                self.skip_quoted_leads,
                _("The lead already has quotations")
            ),
            (lambda l: l.type in ['lead', False], True, _("The lead is in lead state")),
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
                invalid_leads_res += self._create_failed_lead_lines(tmp_invalid_leads, error_msg)
                filtered_leads_res -= tmp_invalid_leads

        return (filtered_leads_res, invalid_leads_res)

    def _send_mail(self, template, quote_ids):
        for quote in quote_ids:
            template.send_mail(quote.id)
            quote.state = "sent"

    def _create_quotations(self, lead_ids):
        failed_lead_line_ids = self.env['crm.sale.automatic.quotation.wizard.line']
        created_quote_ids = self.env['sale.order']
        for rec in lead_ids:
            try:
                created_quote_ids += rec._action_generate_automatic_quotation(
                    from_wizard=True
                )
            except ValidationError as e:
                failed_lead_line_ids+=self._create_failed_lead_lines(rec, str(e))
        if self.send_mail and self.email_template:
            self._send_mail(self.email_template, created_quote_ids)
        return failed_lead_line_ids

    def action_accept(self):
        self.ensure_one()
        if self.wizard_state == "init":
            lead_ids = self.env['crm.lead'].browse(
                self.env.context.get("active_ids")
            )
        elif self.wizard_state == "review":
            lead_ids = self.mapped("failed_lead_line_ids.lead_id")

        (correct_leads, failed_lead_line_ids) = self._filter_leads_and_classify_errors(lead_ids)
        failed_lead_line_ids += self._create_quotations(correct_leads)

        return {
            'name': _('Create automatic quotations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'context': dict(
                self._context,
                default_skip_quoted_leads=self.skip_quoted_leads,
                default_send_mail=self.send_mail,
                default_email_template=self.email_template.id,
                default_failed_lead_line_ids=failed_lead_line_ids.mapped("id"),
                default_wizard_state=("review" if failed_lead_line_ids else "end")
            ),
            'target': 'new',
        }


class CrmSaleAutomaticQuotationWizardLine(models.TransientModel):
    _name = "crm.sale.automatic.quotation.wizard.line"

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='crm.sale.automatic.quotation.wizard',
        readonly=True,
    )
    lead_id = fields.Many2one(
        string='Lead',
        comodel_name='crm.lead',
    )
    error = fields.Char(
        string='Error',
        readonly=True,
    )
