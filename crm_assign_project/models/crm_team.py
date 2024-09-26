# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    automatic_project_assignation = fields.Boolean(
        string="Assign Project", default=False
    )
    automatic_assignation_project_id = fields.Many2one(
        string="Automatically Assigned Project",
        comodel_name="project.project",
    )

    def write(self, vals):
        values = super().write(vals)
        if (
            "automatic_project_assignation" in vals
            or "automatic_assignation_project_id" in vals
        ) and self.alias_id:
            alias_values = self._alias_get_creation_values()
            self.alias_id.write({"alias_defaults": alias_values["alias_defaults"]})
        return values

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        if self.automatic_project_assignation and self.automatic_assignation_project_id:
            values["alias_defaults"][
                "project_id"
            ] = self.automatic_assignation_project_id.id
        elif (
            not self.automatic_project_assignation
            and values.get("alias_defaults")
            and values.get("alias_defaults").get("project_id")
        ):
            values.get("alias_defaults").pop("project_id")
        return values
