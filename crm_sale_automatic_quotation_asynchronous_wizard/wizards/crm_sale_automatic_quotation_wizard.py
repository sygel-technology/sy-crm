# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class CrmSaleAutomaticQuotationWizard(models.TransientModel):
    _inherit = "crm.sale.automatic.quotation.wizard"

    def _send_mail(self, template, quote_ids):
        if not self.env.context.get("delay"):
            self.with_delay(
                channel="root.crm_sale_automatic_quotation_wizard_email"
            )._delay_send_mail(template, quote_ids)
        else:
            return super()._send_mail(template, quote_ids)

    @api.model
    def _delay_send_mail(self, template, quote_ids):
        self.with_context(delay=True)._send_mail(template, quote_ids)
