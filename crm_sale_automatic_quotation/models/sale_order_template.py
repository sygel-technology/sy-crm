# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    crm_automatic_quotation = fields.Boolean(
        string="CRM Automatic Quotation",
    )
    crm_automatic_domain = fields.Char(
        string="Domain",
    )
    cr_automatic_exclude_from_wizard = fields.Boolean(
        string="Exclude from CRM Automatic Quotation Wizard",
    )
