# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    assignment_date = fields.Date(
        string="Assignment date",
        compute="_compute_assignment_date",
        store=True
    )

    @api.depends('user_id')
    def _compute_assignment_date(self):
        """ Sets the assignment date when the opportunity's commercial 
            changes.
        """
        self.filtered(lambda x: x.user_id).write({
            'assignment_date': fields.Date.today()
        })
        self.filtered(lambda x: not x.user_id).write({
            'assignment_date': None
        })
