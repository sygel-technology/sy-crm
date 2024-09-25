# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Transfer Client Portfolio Commissions",
    "summary": "Transfer Client Portfolio Commissions",
    "version": "15.0.1.0.2",
    "category": "crm",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "transfer_client_portfolio",
        "commission",
    ],
    "data": [
        "views/portfolio_transfer_registry_views.xml",
        "wizard/transfer_portfolio_wizard_views.xml",
    ],
}
