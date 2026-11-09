# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    salesperson_planner_reschedule_model = fields.Selection(
        related="company_id.salesperson_planner_reschedule_model",
        readonly=False,
    )
