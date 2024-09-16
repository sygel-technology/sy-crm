# Copyright 2022 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PortfolioTransferRegistry(models.Model):
    _name = "portfolio.transfer.registry"
    _order = "date_transfer desc"
    _description = "Registry of Transfers Clients Portfolios"

    user_made_transfer_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string="Transfer made by",
    )
    date_transfer = fields.Datetime(
        readonly=True,
        string="Transfer Date",
    )
    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string="Previous Salesperson",
    )
    new_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string="New Salesperson",
    )
    list_contacts_ids = fields.Text(
        readonly=True,
        string="List of Transferred Contacts",
    )
    list_opportunity_ids = fields.Text(
        readonly=True,
        string="List of Transferred Opportunities",
    )
    list_activity_ids = fields.Text(
        readonly=True,
        string="List of Transferred Activities",
    )
