# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Salesperson Transfer Portfolio - Phone Calls",
    "version": "18.0.1.0.0",
    "category": "Sales/CRM",
    "summary": "Transfer pending phone calls between salespersons",
    "author": "Sygel",
    "website": "https://github.com/sygel-technology/sy-crm",
    "license": "AGPL-3",
    "depends": [
        "salesperson_transfer_portfolio",
        "crm_phonecall",
    ],
    "data": [
        "wizard/transfer_portfolio_wizard_views.xml",
        "views/portfolio_transfer_registry_views.xml",
    ],
    "installable": True,
    "application": False,
}
