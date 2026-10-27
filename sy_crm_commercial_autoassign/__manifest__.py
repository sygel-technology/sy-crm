# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Commercial Auto Assignment",
    "summary": "Automatically assign salespersons to partners based on ZIP codes",
    "version": "18.0.1.0.0",
    "category": "Sales/CRM",
    "author": "Sygel",
    "website": "https://github.com/sygel-technology/sy-crm",
    "license": "AGPL-3",
    "depends": [
        "base_location",
        "crm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_commercial_autoassign_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "application": False,
}
