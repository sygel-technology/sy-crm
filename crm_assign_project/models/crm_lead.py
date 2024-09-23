# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.onchange("team_id")
    def _onchange_team_id(self):
        if (
            self.team_id
            and self.team_id.automatic_project_assignation
            and self.team_id.automatic_assignation_project_id
        ):
            self.project_id = self.team_id.automatic_assignation_project_id.id
