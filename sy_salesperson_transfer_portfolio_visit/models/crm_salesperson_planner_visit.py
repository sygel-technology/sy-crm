# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmSalespersonPlannerVisit(models.Model):
    _inherit = "crm.salesperson.planner.visit"

    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        string="Previous Salesperson",
        readonly=True,
    )
