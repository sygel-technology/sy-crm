# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.tests import common
from datetime import datetime
from datetime import timedelta
from freezegun import freeze_time
from odoo import exceptions


class TestCrmAutoassign(common.TransactionCase):
    """ Diagram of the equipment, users, stages and opportunities created to 
        perform the tests:

             ---------------------
            |       Team 0        |
             ---------------------
            | team leader: user_0 |
            | member 0: user_0    |
            | member 1: user_1    |
            | member 2: user_2    |
            | opportunities[0:9]  |
             ---------------------

             ---------------------
            |       Team 1        |
             ---------------------
            | team leader: user_3 |
            | member 0: user_3    |
            | member 1: user_4    |
            | member 2: user_5    |
            | opportunities[10:19]|
             ---------------------

             ---------------------
            |       Team 2        |
             ---------------------
            | team leader: user_6 |
            | member 0: user_6    |
            | member 1: user_7    |
            | member 2: user_8    |
            | opportunities[20:29]|
             ---------------------
    """

    @classmethod
    def setUpClass(cls):
        super(TestCrmAutoassign, cls).setUpClass()
        cls.user_ids = cls.env['res.users']
        cls.team_ids = cls.env['crm.team']
        cls.member_ids = cls.env['crm.team.member']
        cls.stage_ids = cls.env['crm.stage']
        cls.opportunity_ids = cls.env['crm.lead']

        # Creation of 9 users
        for i in range(9):
            cls.user_ids |= cls.env['res.users'].sudo().create({
                'name': f'user_{i}',
                'login': f'login_user_{i}'
            })

        # Creation of 3 stages allowing autoassign and 3 teams 
        for i in range(3):
            cls.stage_ids |= cls.env['crm.stage'].create({
                'name': f'stage_{i}',
                'allow_autoassign': True
            })
            cls.team_ids |= cls.env['crm.team'].create({
                'name': f'team_{i}',
                'user_id': cls.user_ids[i*3].id
            })

        # Creation of 9 members. 3 members per team
        for i in range(9):
            cls.member_ids |= cls.env['crm.team.member'].create({
                'user_id': cls.user_ids[i].id,
                'crm_team_id': cls.team_ids[i//3].id,
                'autoassign_opportunities': True if 
                cls.user_ids[i] != cls.team_ids[i//3].user_id else False,
                'max_assignment': 10
            })

        # Creation of 10 opportunities per sales team without user_id
        for i in range(30):
            cls.opportunity_ids |= cls.env['crm.lead'].create({
                'name': f'opportunity_{i}',
                'type': 'opportunity',
                'stage_id': cls.stage_ids[i//10].id,
                'team_id': cls.team_ids[i//10].id,
                'user_id': None
            })

    def test_assignment_optout_true(self):
        """ Checks if the post-instalation script has disabled the Odoo base 
            autoassignment option.
        """
        count = self.env['crm.team.member'].search_count([
            ('assignment_optout', '=', False)
        ])
        self.assertEqual(count, 0)

    def test_assign_manually_autossign_enabled(self):
        """ Manually assign an opportunity to a user who has the
            autossign option activated and check how the assigned
            opportunity counters of the member are incremented.
        """
        user_id = self.user_ids[1]
        member_id = self.member_ids[1]
        opportunity_id = self.opportunity_ids[0]
        opportunity_id.user_id = user_id
        self.assertEqual(member_id.opportunity_autoassign_count, 1)
        self.assertEqual(member_id.opportunity_autoassign_percent, 10.00)

    def test_assign_manually_autossign_disabled(self):
        """ Manually assign an opportunity to a user who has the
            autossign option disabled and check that the opportunity 
            counters of the member remain at zero.
        """
        user_id = self.user_ids[1]
        member_id = self.member_ids[1]
        member_id.autoassign_opportunities = False
        opportunity_id = self.opportunity_ids[0]
        opportunity_id.user_id = user_id
        self.assertEqual(member_id.opportunity_autoassign_count, 0)
        self.assertEqual(member_id.opportunity_autoassign_percent, 0.00)

    def test_change_max_assignment(self):
        """ Assigns two opportunities to a user and lowers the maximum number
            of assignments. The opportunity_autoassign_count should remain
            constant but opportunity_autoassign_percent should be increased.
        """
        opportunity_1 = self.opportunity_ids[0]
        opportunity_2 = self.opportunity_ids[1]
        user_id = self.user_ids[1]
        member_id = self.member_ids[1]
        (opportunity_1 + opportunity_2).write({'user_id': user_id.id})
        self.assertEqual(member_id.opportunity_autoassign_count, 2)
        self.assertEqual(member_id.opportunity_autoassign_percent, 20.00)
        
        member_id.max_assignment = 5
        self.assertEqual(member_id.opportunity_autoassign_count, 2)
        self.assertEqual(member_id.opportunity_autoassign_percent, 40.00)

    def test_change_assignment_days(self):
        """ Test for the change of autoassign days
            1. Lower days of autoassignment.
            2. Two opportunities are assigned to a user yesterday
            3. One opportunity is assigned to the same user today
            4. Assignment days are increased
            5. Check how the counters are incremented
        """
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        opt_id_yesterday_1 = self.opportunity_ids[0]
        opt_id_yesterday_2 = self.opportunity_ids[1]
        opt_id_today_1 = self.opportunity_ids[2]
        user_id = self.user_ids[1]
        member_id = self.member_ids[1]
        with freeze_time(yesterday):
            opt_id_yesterday_1.user_id = user_id
            opt_id_yesterday_2.user_id = user_id
            self.assertEqual(member_id.opportunity_autoassign_count, 2)
            self.assertEqual(member_id.opportunity_autoassign_percent, 20.00)
        
        opt_id_today_1.user_id = user_id
        member_id.invalidate_cache(fnames=['opportunity_autoassign_count'])
        self.assertEqual(member_id.opportunity_autoassign_count, 1)
        self.assertEqual(member_id.opportunity_autoassign_percent, 10.00)

        member_id.assignment_days = 1
        self.assertEqual(member_id.opportunity_autoassign_count, 3)
        self.assertEqual(member_id.opportunity_autoassign_percent, 30.00)

    def test_change_opportunity_team(self):
        """ An opportunity is assigned to a user.
            Remove the team from the opportunity and check that the 
            team member has zero counters.
        """
        opportunity_id = self.opportunity_ids[0]
        user_id = self.user_ids[1]
        member_id = self.member_ids[1]
        opportunity_id.user_id = user_id.id
        self.assertEqual(member_id.opportunity_autoassign_count, 1)
        self.assertEqual(member_id.opportunity_autoassign_percent, 10.00)
        opportunity_id.team_id = None
        member_id.invalidate_cache(fnames=['opportunity_autoassign_count'])
        self.assertEqual(member_id.opportunity_autoassign_count, 0)
        self.assertEqual(member_id.opportunity_autoassign_percent, 0.00)

    def test_constraint_team_leader_not_autoassign_opportunities(self):
        """ Checks that a teamleader cannot have the autoassignment option 
            enabled. 
        """
        member_id = self.member_ids[0]
        with self.assertRaises(exceptions.ValidationError): 
            member_id.autoassign_opportunities = True

    def test_constraint_change_team_leader_not_autoassign_opportunities(self):
        """ Checks that the team leader does not have the autoassignment 
            option enabled. 
        """
        team_id = self.team_ids[0]
        user_id = self.user_ids[1]
        with self.assertRaises(exceptions.ValidationError): 
            team_id.user_id = user_id

    def test_autoassing_without_opportunities_in_not_allowed_stage(self):
        """ Automatic opportunity assignment without any opportunity in an
            allowed state. The option to allow auto assignment of the stages 
            is disabled and the planned auto assignment function is called.
        """
        self.stage_ids.write({'allow_autoassign': False})
        self.env.ref(
            'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
        for sel in self.member_ids:
            self.assertEqual(sel.opportunity_autoassign_count, 0)
            self.assertEqual(sel.opportunity_autoassign_percent, 0.00)
    
    # def test_autoassing_opportunities(self):
    #     """ Checks the mass assignment of opportunities in a balanced way by 
    #         calling for scheduled action.
    #     """
    #     self.env.ref(
    #         'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])
    #     team_leader_ids = self.team_ids.mapped('user_id')
    #     for sel in self.member_ids.filtered(
    #      lambda x: x.user_id.id not in team_leader_ids.ids):
    #         self.assertEqual(sel.opportunity_autoassign_count, 5)
    #         self.assertEqual(sel.opportunity_autoassign_percent, 50.00)
    
    # def test_autoassing_opportunities_with_team_leader(self):
    #     """ Assignment of opportunities with the team leader. 
    #     """
    #     for opportunity in self.opportunity_ids:
    #         opportunity.user_id = opportunity.team_id.user_id
    #     self.env.ref(
    #         'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])
    #     team_leader_ids = self.team_ids.mapped('user_id')
    #     for sel in self.member_ids.filtered(
    #      lambda x: x.user_id.id not in team_leader_ids.ids):
    #         self.assertEqual(sel.opportunity_autoassign_count, 5)
    #         self.assertEqual(sel.opportunity_autoassign_percent, 50.00)
    
    # def test_autoassing_opportunities_with_domain(self):
    #     """ Assignment of opportunities with domain in one of the members.
    #     """
    #     partner_1 = self.env['res.partner'].create({
    #         'name': 'partner_1'
    #     })
    #     member_1 = self.member_ids[1]
    #     member_2 = self.member_ids[2]
    #     for opportunity in self.opportunity_ids:
    #         opportunity.partner_id = partner_1
    #     member_1.assignment_domain_custom = "[['partner_id.name', '!=', 'partner_1']]"
    #     self.env.ref(
    #         'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])

    #     self.assertEqual(member_1.opportunity_autoassign_count, 0)
    #     self.assertEqual(member_1.opportunity_autoassign_percent, 0.00)

    #     self.assertEqual(member_2.opportunity_autoassign_count, 10)
    #     self.assertEqual(member_2.opportunity_autoassign_percent, 100.00)

    # def test_autoassing_opportunities_form_team(self):
    #     """ Massive allocation of opportunities in a balanced way from the Sales team 
    #     """
    #     member_1 = self.member_ids[1]
    #     member_2 = self.member_ids[2]
    #     team = self.team_ids[0]
    #     team.action_autoassign_opportunities()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])
    #     self.assertEqual(member_1.opportunity_autoassign_count, 5)
    #     self.assertEqual(member_1.opportunity_autoassign_percent, 50.00)

    #     self.assertEqual(member_2.opportunity_autoassign_count, 5)
    #     self.assertEqual(member_2.opportunity_autoassign_percent, 50.00)

    # def test_autoassing_opportunities_with_team_leader_from_team(self):
    #     """ Massive allocation of opportunities in a balanced way from the 
    #         Sales team and with team_leader
    #     """
    #     member_1 = self.member_ids[1]
    #     member_2 = self.member_ids[2]
    #     team = self.team_ids[0]
    #     for opportunity in self.opportunity_ids.filtered(
    #      lambda x: x.team_id.id == team.id):
    #         opportunity.user_id = opportunity.team_id.user_id
    #     team.action_autoassign_opportunities()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])
    #     self.assertEqual(member_1.opportunity_autoassign_count, 5)
    #     self.assertEqual(member_1.opportunity_autoassign_percent, 50.00)

    #     self.assertEqual(member_2.opportunity_autoassign_count, 5)
    #     self.assertEqual(member_2.opportunity_autoassign_percent, 50.00)

    # def test_autoassing_opportunities_with_domain_from_team(self):
    #     """ Assignment of opportunities with dominance in one of the members.
    #     """
    #     partner_1 = self.env['res.partner'].sudo().create({
    #         'name': 'partner_1'
    #     })
    #     member_1 = self.member_ids[1]
    #     member_2 = self.member_ids[2]
    #     team = self.team_ids[0]
    #     for opportunity in self.opportunity_ids:
    #         opportunity.partner_id = partner_1
    #     member_1.assignment_domain_custom = "[['partner_id.name', '!=', 'partner_1']]"
    #     team.action_autoassign_opportunities()
    #     self.member_ids.invalidate_cache(
    #         fnames=['opportunity_autoassign_count'])

    #     self.assertEqual(member_1.opportunity_autoassign_count, 0)
    #     self.assertEqual(member_1.opportunity_autoassign_percent, 0.00)

    #     self.assertEqual(member_2.opportunity_autoassign_count, 10)
    #     self.assertEqual(member_2.opportunity_autoassign_percent, 100.00)

    # def test_autoassign_opportunities_and_move_opportunity(self):
    #     """ Check that if there is a stage after the autoassignment the 
    #         opportunity moves to this stage.
    #     """
    #     opportunity_1 = self.opportunity_ids[0]
    #     opportunity_2 = self.opportunity_ids[10]
    #     team_1 = self.team_ids[0]
    #     stage = self.env['crm.stage'].create({
    #             'name': 'stage_after_autoassign',
    #         })
    #     team_1.stage_after_autoassign = stage
    #     self.env.ref(
    #         'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
    #     self.assertEqual(
    #         opportunity_1.stage_id.id, team_1.stage_after_autoassign.id
    #     )
    #     self.assertEqual(opportunity_2.stage_id.id, self.stage_ids[1].id)

    # def test_autoassing_opportunities_from_cron_and_team(self):
    #     """ Executes the scheduled action and an attempt is made to execute it
    #         from the team.
    #     """
    #     opportunity_ids = self.env['crm.lead']
    #     team = self.team_ids[0]
    #     for i in range(2000):
    #         opportunity_ids |= self.env['crm.lead'].create({
    #             'name': f'opportunity_{i}',
    #             'type': 'opportunity',
    #             'stage_id': self.stage_ids[0].id,
    #             'team_id': team.id,
    #             'user_id': None
    #         })
    #     self.env.ref(
    #         'crm_autoassign.crm_autoassign_cron').method_direct_trigger()
    #     with self.assertRaises(exceptions.UserError):
    #         team.action_autoassign_opportunities()
