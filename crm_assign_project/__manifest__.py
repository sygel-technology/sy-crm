# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Assign Project",
    "summary": "Automatically assign project to CRM lead.",
    "version": "17.0.1.0.0",
    "category": "CRM",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["crm", "sales_team", "crm_timesheet"],
    "data": [
        "views/crm_team_views.xml",
    ],
}
