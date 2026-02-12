# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Salesperson Transfer Portfolio Commission",
    "summary": "Salesperson Transfer Portfolio Commission",
    "version": "18.0.1.0.0",
    "category": "crm",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "salesperson_transfer_portfolio",
        "commission_oca",
    ],
    "data": [
        "views/portfolio_transfer_registry_views.xml",
        "wizard/transfer_portfolio_wizard_views.xml",
    ],
}
