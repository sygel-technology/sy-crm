# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import psycopg2


class Team(models.Model):
    _inherit = "crm.team"

    any_member_autoassign = fields.Boolean(
        string="Any member with autoassign",
        compute="_compute_any_member_autoassign",
        store=True
    )
    stage_after_autoassign = fields.Many2one(
        comodel_name="crm.stage",
        string="Stage after autoassign",
        help="Stage where the opportunity will move after autoassign. "
        "If there is none, it will not move stage."
    )

    @api.depends('crm_team_member_ids.autoassign_opportunities')
    def _compute_any_member_autoassign(self):
        """ Checks if there are any members in the team with the auto-assignment
            option selected.
        """
        for sel in self:
            sel.any_member_autoassign = bool(sel.crm_team_member_ids.filtered(
                lambda x: x.autoassign_opportunities
            ))

    def action_autoassign_opportunities(self):
        """ Runs the automatic opportunity assigner for a specific team.
            Before that, checks that the planned action is not running.
        """
        action_id = self.env.ref("crm_autoassign.crm_autoassign_cron")
        try:
            self._cr.execute(
                "SELECT id FROM ir_cron WHERE id in ({}) FOR UPDATE NOWAIT".
                format(action_id.id)
            )
        except psycopg2.OperationalError:
            raise UserError(_(
                "Odoo is currently executing the planned action of opportunity"
                " allocation. Please try again later."
            ))
        for sel in self:
            sel.env['crm.team.member'].action_autoassign_opportunities(sel)

    @api.constrains("user_id")
    def checks_team_leader(self):
        """ Checks that the team leader does not have the autoassign option 
            checked if he is also a team member.
        """
        for sel in self.filtered(lambda x: x.user_id in x.member_ids):
            if sel.crm_team_member_ids.filtered(
             lambda x: x.user_id == sel.user_id).autoassign_opportunities:
                raise ValidationError(_(
                    "The team leader cannot autoassign the opportunities. "
                    "Uncheck the option for automatic assignment opportunities"
                    " for member {} or choose another member."
                    ).format(sel.user_id.name)
                )
