# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PortfolioTransferRegistry(models.Model):
    _inherit = "portfolio.transfer.registry"

    list_phonecall_ids = fields.Text(
        readonly=True,
        string="List of Transferred Phone Calls",
    )
