# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "CRM Salesperson Planner Extended",
    "summary": "Extend salesperson planner rescheduling functionality",
    "version": "18.0.1.0.0",
    "author": "Sygel",
    "category": "crm",
    "website": "https://github.com/sygel-technology/sy-crm",
    "depends": [
        "crm_salesperson_planner",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "wizard/crm_salesperson_planner_visit_close_wiz_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
