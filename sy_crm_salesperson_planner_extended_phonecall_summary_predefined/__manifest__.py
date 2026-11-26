# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "CRM Salesperson Planner Extended Phonecall Summary Predefined",
    "summary": "Use predefined summaries when rescheduling visits as phone calls",
    "version": "18.0.1.0.0",
    "author": "Sygel",
    "category": "crm",
    "website": "https://github.com/sygel-technology/sy-crm",
    "depends": [
        "sy_crm_salesperson_planner_extended_phonecall",
        "crm_phonecall_summary_predefined",
    ],
    "data": [
        "wizard/crm_salesperson_planner_visit_close_wiz_views.xml",
    ],
    "license": "AGPL-3",
    "auto_install": True,
    "installable": True,
}
