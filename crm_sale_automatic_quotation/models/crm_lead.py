# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _get_crm_automatic_quotation_values(self, quotation_template):
        self.ensure_one()
        values = {
            'opportunity_id': self.id,
            'partner_id': self.partner_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'origin': self.name,
            'source_id': self.source_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'sale_order_template_id': quotation_template.id
        }
        return values

    def _recompute_quotation_lines(self, order_line):
        """
            Inherit to modify the fields of the automatic quotations lines.
        """
        return order_line

    def action_generate_automatic_quotation(self):
        self.ensure_one()
        res = self.env['sale.order']
        for template in self.env['sale.order.template'].search([
                ('crm_automatic_quotation', '=', True)]):
            vals_list = []
            domain = template.crm_automatic_domain
            if domain:
                domain = expression.AND([
                    safe_eval(domain), [("id", "=", self.id)]
                ])
            if not domain or self.env['crm.lead'].search(domain, limit=1):
                vals_list = self._get_crm_automatic_quotation_values(template)
            if vals_list:
                quotation_id = res.create(vals_list)
                # To update the quotation template fields in the quotation
                quotation_id.with_context(dict(
                    self._context, is_crm_automatic_quotation=True)
                ).onchange_sale_order_template_id()
                self._recompute_quotation_lines(quotation_id.order_line)
                res |= quotation_id
        if not res and not self.env.context.get("skip_no_template_err", False):
            raise ValidationError(_(
                "There are no quotation templates for this opportunity. "
                "Set up a quotation template and try again."
            ))
        return self.action_view_sale_quotation()
