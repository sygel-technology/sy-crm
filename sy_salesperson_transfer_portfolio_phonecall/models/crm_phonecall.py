# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    user_id = fields.Many2one(tracking=True)

    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        string="Previous Salesperson",
        readonly=True,
    )
