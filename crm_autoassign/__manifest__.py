# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Autoassign",
    "summary": "CRM Autoassign",
    "version": "15.0.1.0.1",
    "category": "CRM",
    "website": "https://www.sygel.es",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'sales_team',
        'crm'
    ],   
    "data": [
        "data/cron.xml",
        "views/crm_team_views.xml",
        "views/crm_team_member_views.xml",
        "views/crm_stage_views.xml"
    ],
    "post_init_hook": "post_init_hook",
}
