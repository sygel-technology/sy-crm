# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Sale Automatic Quotation",
    "summary": "CRM Sale Automatic Quotation",
    "version": "18.0.1.0.0",
    "category": "CRM",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "crm",
        "sale",
        "sale_management",
        "sale_crm",
        "sales_team",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/mail_activity_type.xml",
        "views/sale_order_template_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_stage_views.xml",
        "wizards/crm_sale_automatic_quotation_wizard.xml",
    ],
}
