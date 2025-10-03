# Copyright 2023 Ángel García de la Chica <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Group Sale Salesman Extension",
    "summary": "CRM Group Sale Salesman Extension",
    "version": "18.0.1.0.0",
    "category": "CRM",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "crm", "sales_team"],
    "data": ["security/crm_sale_record_rules.xml"],
}
