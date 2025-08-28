# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string="Previous Salesperson",
    )
