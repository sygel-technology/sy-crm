# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestCrmSalespersonPlannerExtendedPhonecall(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.company.salesperson_planner_reschedule_model = "phonecall"
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Phonecall Partner",
            }
        )
        cls.team = cls.env["crm.team"].create(
            {
                "name": "Test Phonecall Sales Team",
            }
        )
        cls.opportunity = cls.env["crm.lead"].create(
            {
                "name": "Test Phonecall Opportunity",
                "type": "opportunity",
                "partner_id": cls.partner.id,
                "team_id": cls.team.id,
                "company_id": cls.company.id,
            }
        )
        cls.close_reason = cls.env["crm.salesperson.planner.visit.close.reason"].create(
            {
                "name": "Test Phonecall Close Reason",
                "close_type": "cancel",
                "reschedule": True,
            }
        )
        cls.visit = cls.env["crm.salesperson.planner.visit"].create(
            {
                "partner_id": cls.partner.id,
                "user_id": cls.env.user.id,
                "company_id": cls.company.id,
                "date": "2026-11-10",
                "sequence": 20,
                "opportunity_ids": [
                    (6, 0, cls.opportunity.ids),
                ],
            }
        )
        cls.visit.action_confirm()

    def test_reschedule_phonecall_with_opportunity(self):
        phonecall_count = self.env["crm.phonecall"].search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "phonecall",
                    "phonecall_date": "2026-11-15 10:30:00",
                    "phonecall_name": "Test Rescheduled Phonecall",
                    "phonecall_description": "Contact the customer again.",
                    "phonecall_opportunity_id": self.opportunity.id,
                    "notes": "Customer was not available.",
                }
            )
        )
        wizard.action_close_reason_apply()
        phonecall = self.env["crm.phonecall"].search(
            [("name", "=", "Test Rescheduled Phonecall")]
        )
        self.assertEqual(self.visit.state, "cancel")
        self.assertEqual(self.visit.close_reason_id, self.close_reason)
        self.assertEqual(
            self.env["crm.phonecall"].search_count([]),
            phonecall_count + 1,
        )
        self.assertEqual(len(phonecall), 1)
        self.assertEqual(phonecall.opportunity_id, self.opportunity)
        self.assertEqual(phonecall.team_id, self.team)
        self.assertEqual(phonecall.partner_id, self.partner)
        self.assertEqual(phonecall.user_id, self.visit.user_id)
        self.assertEqual(phonecall.company_id, self.company)
        self.assertEqual(
            phonecall.date,
            fields.Datetime.to_datetime("2026-11-15 10:30:00"),
        )
        self.assertEqual(phonecall.state, "open")
        self.assertIn("Contact the customer again.", phonecall.description)
        self.assertIn(self.close_reason.name, phonecall.description)
        self.assertIn("Customer was not available.", phonecall.description)

    def test_reschedule_phonecall_without_opportunity(self):
        self.visit.opportunity_ids = [fields.Command.clear()]
        phonecall_count = self.env["crm.phonecall"].search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "phonecall",
                    "phonecall_date": "2026-11-15 10:30:00",
                    "phonecall_name": "Test Phonecall Without Opportunity",
                    "phonecall_description": "Contact the customer again.",
                    "notes": "Customer was not available.",
                }
            )
        )
        wizard.action_close_reason_apply()
        phonecall = self.env["crm.phonecall"].search(
            [("name", "=", "Test Phonecall Without Opportunity")]
        )
        self.assertEqual(self.visit.state, "cancel")
        self.assertEqual(self.visit.close_reason_id, self.close_reason)
        self.assertEqual(
            self.env["crm.phonecall"].search_count([]),
            phonecall_count + 1,
        )
        self.assertEqual(len(phonecall), 1)
        self.assertFalse(phonecall.opportunity_id)
        self.assertFalse(phonecall.team_id)
        self.assertEqual(phonecall.partner_id, self.partner)
        self.assertEqual(phonecall.user_id, self.visit.user_id)
        self.assertEqual(phonecall.company_id, self.company)
        self.assertEqual(
            phonecall.date,
            fields.Datetime.to_datetime("2026-11-15 10:30:00"),
        )
        self.assertEqual(phonecall.state, "open")
        self.assertIn("Contact the customer again.", phonecall.description)
        self.assertIn(self.close_reason.name, phonecall.description)
        self.assertIn("Customer was not available.", phonecall.description)

    def test_reschedule_phonecall_multiple_opportunities(self):
        second_team = self.env["crm.team"].create(
            {
                "name": "Second Test Sales Team",
            }
        )
        second_opportunity = self.env["crm.lead"].create(
            {
                "name": "Second Test Opportunity",
                "type": "opportunity",
                "partner_id": self.partner.id,
                "team_id": second_team.id,
                "company_id": self.company.id,
            }
        )
        self.visit.opportunity_ids = [
            fields.Command.link(second_opportunity.id),
        ]
        phonecall_count = self.env["crm.phonecall"].search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "phonecall",
                    "phonecall_date": "2026-11-15 10:30:00",
                    "phonecall_name": "Test Phonecall Multiple Opportunities",
                    "phonecall_description": "Follow up on the selected opportunity.",
                    "phonecall_opportunity_id": second_opportunity.id,
                    "notes": "Customer was not available.",
                }
            )
        )
        self.assertEqual(
            wizard.phonecall_opportunity_ids,
            self.opportunity | second_opportunity,
        )
        wizard.action_close_reason_apply()
        phonecall = self.env["crm.phonecall"].search(
            [("name", "=", "Test Phonecall Multiple Opportunities")]
        )
        self.assertEqual(self.visit.state, "cancel")
        self.assertEqual(
            self.env["crm.phonecall"].search_count([]),
            phonecall_count + 1,
        )
        self.assertEqual(len(phonecall), 1)
        self.assertEqual(phonecall.opportunity_id, second_opportunity)
        self.assertEqual(phonecall.team_id, second_team)
        self.assertEqual(phonecall.partner_id, self.partner)
        self.assertEqual(phonecall.company_id, self.company)
        self.assertEqual(phonecall.state, "open")

    def test_default_phonecall_opportunity(self):
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "phonecall",
                    "phonecall_date": "2026-11-15 10:30:00",
                    "phonecall_name": "Test Default Phonecall Opportunity",
                }
            )
        )
        self.assertEqual(
            wizard.phonecall_opportunity_ids,
            self.opportunity,
        )
        self.assertEqual(
            wizard.phonecall_opportunity_id,
            self.opportunity,
        )
        wizard.action_close_reason_apply()
        phonecall = self.env["crm.phonecall"].search(
            [("name", "=", "Test Default Phonecall Opportunity")]
        )
        self.assertEqual(len(phonecall), 1)
        self.assertEqual(phonecall.opportunity_id, self.opportunity)
        self.assertEqual(phonecall.team_id, self.team)
        self.assertEqual(self.visit.state, "cancel")

    def test_default_reschedule_model_multicompany(self):
        second_company = self.env["res.company"].create(
            {
                "name": "Second Test Company",
                "salesperson_planner_reschedule_model": "visit",
            }
        )
        wizard_model = self.env["crm.salesperson.planner.visit.close.wiz"]
        wizard_phonecall = wizard_model.with_company(self.company).create(
            {
                "reason_id": self.close_reason.id,
            }
        )
        wizard_visit = wizard_model.with_company(second_company).create(
            {
                "reason_id": self.close_reason.id,
            }
        )
        self.assertEqual(
            self.company.salesperson_planner_reschedule_model,
            "phonecall",
        )
        self.assertEqual(
            second_company.salesperson_planner_reschedule_model,
            "visit",
        )
        self.assertEqual(wizard_phonecall.reschedule_model, "phonecall")
        self.assertEqual(wizard_visit.reschedule_model, "visit")

    def test_reschedule_visit(self):
        visit_count = self.env["crm.salesperson.planner.visit"].search_count([])
        phonecall_count = self.env["crm.phonecall"].search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "visit",
                    "new_date": "2026-11-15",
                    "new_sequence": 30,
                    "notes": "Customer was not available.",
                }
            )
        )
        wizard.action_close_reason_apply()
        new_visit = self.env["crm.salesperson.planner.visit"].search(
            [
                ("id", "!=", self.visit.id),
                ("partner_id", "=", self.partner.id),
                ("date", "=", "2026-11-15"),
                ("sequence", "=", 30),
            ]
        )
        self.assertEqual(self.visit.state, "cancel")
        self.assertEqual(self.visit.close_reason_id, self.close_reason)
        self.assertEqual(
            self.env["crm.salesperson.planner.visit"].search_count([]),
            visit_count + 1,
        )
        self.assertEqual(
            self.env["crm.phonecall"].search_count([]),
            phonecall_count,
        )
        self.assertEqual(len(new_visit), 1)
        self.assertEqual(new_visit.state, "confirm")
        self.assertEqual(new_visit.partner_id, self.partner)
        self.assertEqual(new_visit.user_id, self.visit.user_id)
        self.assertEqual(new_visit.company_id, self.company)
        self.assertEqual(new_visit.opportunity_ids, self.opportunity)
        self.assertEqual(new_visit.sequence, 30)
        self.assertTrue(new_visit.calendar_event_id)

    def test_close_without_reschedule(self):
        visit_count = self.env["crm.salesperson.planner.visit"].search_count([])
        phonecall_count = self.env["crm.phonecall"].search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": False,
                    "reschedule_model": "phonecall",
                    "notes": "Customer was not available.",
                }
            )
        )
        wizard.action_close_reason_apply()
        self.assertEqual(self.visit.state, "cancel")
        self.assertEqual(self.visit.close_reason_id, self.close_reason)
        self.assertEqual(
            self.visit.close_reason_notes,
            "Customer was not available.",
        )
        self.assertEqual(
            self.env["crm.salesperson.planner.visit"].search_count([]),
            visit_count,
        )
        self.assertEqual(
            self.env["crm.phonecall"].search_count([]),
            phonecall_count,
        )
