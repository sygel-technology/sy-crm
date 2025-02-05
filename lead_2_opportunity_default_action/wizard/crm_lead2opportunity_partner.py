# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    def _get_default_action(self):
        self.ensure_one()
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lead_2_opportunity_default_action.default")
        )

    def _compute_name(self):
        default_val_param = self._get_default_action()
        if default_val_param and default_val_param in ["convert", "merge"]:
            ret_vals = self.name = default_val_param
        else:
            ret_vals = super()._compute_name()
        return ret_vals
