# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Sale Automatic Quotation",
    "summary": "CRM Sale Automatic Quotation",
    "version": "15.0.1.0.0",
    "category": "CRM",
    "website": "https://www.sygel.es",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'crm',
        'sale',
        'sale_management',
        'sale_crm',
    ],   
    "data": [
       "views/sale_order_template_views.xml",
       "views/crm_lead_views.xml"
    ],
}
