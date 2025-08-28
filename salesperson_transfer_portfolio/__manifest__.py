# Copyright 2022 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Salesperson Transfer Portfolio",
    "summary": "Transfer Client Portfolio Between Salespersons.",
    "version": "18.0.1.0.0",
    "category": "crm",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "crm",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/crm_lead_views.xml",
        "views/portfolio_transfer_registry_views.xml",
        "views/crm_stage_views.xml",
        "views/res_config_settings_view.xml",
        "wizard/transfer_portfolio_wizard_views.xml",
    ],
}
