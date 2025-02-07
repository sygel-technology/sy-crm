# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Lead2OpportunityMassConvert(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner.mass"

    def _compute_name(self):
        default_val_param = self._get_default_action()
        if default_val_param and default_val_param in ["convert", "merge"]:
            ret_vals = self.name = default_val_param
        else:
            ret_vals = super()._compute_name()
        return ret_vals
