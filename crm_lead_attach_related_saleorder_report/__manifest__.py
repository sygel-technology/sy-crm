# Copyright 2020 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Crm Lead Attach Related Saleorder Report",
    "version": "17.0.1.1.0",
    "category": "Sale",
    "summary": "Allow to attach sale documents into the opportunity and send them.",
    "author": "Sygel",
    "website": "https://github.com/sygel-technology/sy-crm",
    "license": "AGPL-3",
    "depends": [
        "sale_crm",
    ],
    "data": ["views/crm_lead.xml", "views/mail_compose_message.xml"],
    "installable": True,
}
