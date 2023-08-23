# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Stage(models.Model):
    _inherit = "crm.stage"

    allow_autoassign = fields.Boolean(
        string='Allow autoassign',
        default=False,
        help="The opportunity that is at this stage with an assigned sales "
        "team and without a salesperson may be assigned automatically."
    )
