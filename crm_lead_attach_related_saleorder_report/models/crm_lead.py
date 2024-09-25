# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_send_documents_sale(self):
        """
        This function opens a window to compose an email.
        """
        self.ensure_one()
        ctx = {
            "default_model": "crm.lead",
            "default_res_ids": self.ids,
            "default_composition_mode": "comment",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "target": "new",
            "context": ctx,
        }
