# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "CRM Sale Automatic Quotation Asynchronous Wizard",
    "summary": "Speed up the CRM Sale Automatic Quotation Wizard",
    "version": "18.0.1.0.0",
    "category": "CRM",
    "website": "https://github.com/sygel-technology/sy-crm",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "crm_sale_automatic_quotation",
        "queue_job",
    ],
    "data": [
        "wizards/crm_sale_automatic_quotation_wizard.xml",
    ],
}
