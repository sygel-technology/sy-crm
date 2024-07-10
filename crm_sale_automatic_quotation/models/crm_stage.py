# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrmStage(models.Model):
    _inherit = "crm.stage"

    crm_automatic_wizard_dest_stage = fields.Boolean(
        string="Dest. Stage in Automatic Quotations Wizard",
        help="If quotations are created for a lead"
        " with the automatic quotations wizard,"
        " the lead will be updated to this stage."
        " Only one stage can have this option per crm team",
    )

    @api.model
    def _get_crm_automatic_wizard_dest_stage(self, team_id):
        return self.env["crm.stage"].search(
            [
                ("crm_automatic_wizard_dest_stage", "!=", False),
                "|",
                ("team_id", "=", team_id.id),
                ("team_id", "=", False),
            ],
            limit=1,
        )
