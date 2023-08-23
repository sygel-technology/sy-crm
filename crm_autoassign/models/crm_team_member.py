# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.tools.safe_eval import safe_eval
import threading


class CrmTeamMember(models.Model):
    _inherit = "crm.team.member"

    assignment_optout = fields.Boolean(
        default=True
    )
    autoassign_opportunities = fields.Boolean(
        string='Autoassign Opportunities',
        default=False
    )
    assignment_days = fields.Integer(
        string='Assignement Days',
        default=0
    )
    max_assignment = fields.Integer(
        string='Maximum number of assignments',
        help="Maximum number of assignments in the last 'Assignment days'"
    )
    assignment_domain_custom = fields.Char(
        string="Domain"
    )
    opportunity_autoassign_count = fields.Integer(
        string="Assigned Opportunities",
        compute="_compute_opportunity_count"
    )
    opportunity_autoassign_percent = fields.Float(
        string="Percentage of Opportunities",
        compute="_compute_opportunity_count"
    )

    def action_view_opportunities(self):
        """ Returns the action with the opportunities automatically assigned 
            to the team member in the configured period
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "crm.crm_lead_opportunities"
        )
        action['context'] = {
            'search_default_type': 'opportunity',
        }
        now = fields.Datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        )
        action['domain'] = [
            ('user_id', '=', self.user_id.id),
            ('assignment_date', '>=', now - timedelta(
                    days=self.assignment_days)),
            ('assignment_date', '<=', now)
        ]
        return action

    @api.depends('assignment_days', 'max_assignment')
    def _compute_opportunity_count(self):
        """ Computes the number of automatically assigned opportunities and the
            occupancy rate (opportunity_autoassign_percent) of the team member.
        """
        now = fields.Datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=0
        )
        for sel in self.filtered(lambda x: x.autoassign_opportunities):
            percent = 100.00
            count_opt_ids = self.env['crm.lead'].search_count([
                ('user_id', '=', sel.user_id.id),
                ('team_id', '=', sel.crm_team_id.id),
                ('assignment_date', '>=', now - timedelta(
                    days=sel.assignment_days)),
                ('assignment_date', '<=', now)
            ])
            if sel.max_assignment > 0:
                percent = (count_opt_ids / sel.max_assignment)*100
            sel.write({
                'opportunity_autoassign_count': count_opt_ids,
                'opportunity_autoassign_percent': percent
            })
        self.filtered(lambda x: not x.autoassign_opportunities).write({
            'opportunity_autoassign_count': 0,
            'opportunity_autoassign_percent': 0.00
        })

    def _get_autoassign_teams_members(self, opportunity):
        """ Gets the team members who can be assigned the opportunity. """
        res = self.env['crm.team.member']
        member_ids = opportunity.team_id.crm_team_member_ids
        for member in member_ids.filtered(
            lambda x: x.autoassign_opportunities and
            x.opportunity_autoassign_percent < 100 and
            x.user_id != opportunity.team_id.user_id
        ):
            if not member.assignment_domain_custom or\
                opportunity in self.env['crm.lead'].search(
                    safe_eval(member.assignment_domain_custom)):
                res |= member
        return res
    
    def action_autoassign_opportunities(self, team_id=None):
        """ Searches for opportunities to be assigned and assigns them to 
            available team members.
        """
        auto_commit = not getattr(threading.current_thread(), 'testing', False)
        domain = [
            ('type', '=', 'opportunity'),
            ('team_id', '!=', None),
            ('stage_id.allow_autoassign', '=', True),
        ]
        if team_id:
            domain = [
                ('type', '=', 'opportunity'),
                ('team_id', '=', team_id.id),
                ('stage_id.allow_autoassign', '=', True),
            ]
        opportunity_ids = self.env['crm.lead'].search(domain).filtered(
            lambda x: not x.user_id or x.user_id == x.team_id.user_id
        )
        for opportunity in opportunity_ids:
            member_ids = self._get_autoassign_teams_members(opportunity)
            if member_ids:
                member_id = member_ids.sorted(
                    lambda x: x.opportunity_autoassign_percent,
                    reverse=False)[0]
                vals = {
                    'user_id': member_id.user_id.id,
                    'team_id': opportunity.team_id.id
                }
                if opportunity.team_id.stage_after_autoassign:
                    vals['stage_id'] = opportunity.team_id.\
                        stage_after_autoassign.id
                opportunity.write(vals)
                if auto_commit:
                    self._cr.commit()

    @api.constrains("autoassign_opportunities")
    def checks_team_manager(self):
        """ Checks that if is the option of autoassign opportunities checked 
            is not also the team leader.
        """
        for sel in self.filtered(
            lambda x: x.autoassign_opportunities and 
                x.user_id == x.crm_team_id.user_id):
            raise ValidationError(_(
                "Member {} cannot autoassign opportunities because he is the "
                "leader of team {}. The team leader's opportunities must be "
                "assigned manually."
                ).format(sel.user_id.name, sel.crm_team_id.name)
            )
