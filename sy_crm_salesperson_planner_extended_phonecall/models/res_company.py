# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    salesperson_planner_reschedule_model = fields.Selection(
        selection_add=[
            ("phonecall", "Phone Calls"),
        ],
        ondelete={"phonecall": "set default"},
    )
