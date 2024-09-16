# Copyright 2022 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Stage(models.Model):
    _inherit = "crm.stage"

    allow_transfer_opportunity = fields.Boolean(
        default=True,
        string="Allow transfer at this stage",
    )
