# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PortfolioTransferRegistry(models.Model):
    _inherit = "portfolio.transfer.registry"

    list_agents_ids = fields.Text(
        readonly=True,
        string="List of Transferred Agents",
    )
    transferred_agents = fields.Boolean(
        readonly=True,
    )
