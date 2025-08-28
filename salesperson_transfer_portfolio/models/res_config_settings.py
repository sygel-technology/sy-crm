# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    transfer_activities = fields.Boolean(
        string="Transfer Salesperson Activities",
        related="company_id.transfer_activities",
        readonly=False,
    )
