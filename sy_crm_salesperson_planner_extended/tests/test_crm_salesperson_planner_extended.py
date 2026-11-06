# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCrmSalespersonPlannerExtended(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        cls.company.salesperson_planner_reschedule_model = "visit"

        cls.close_reason = cls.env["crm.salesperson.planner.visit.close.reason"].create(
            {
                "name": "Test Reschedule Reason",
                "close_type": "cancel",
                "reschedule": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Reschedule Partner",
            }
        )
        cls.visit = cls.env["crm.salesperson.planner.visit"].create(
            {
                "partner_id": cls.partner.id,
                "date": "2026-11-10",
                "sequence": 20,
                "company_id": cls.company.id,
                "user_id": cls.env.user.id,
            }
        )
        cls.visit.action_confirm()

    def test_default_reschedule_model(self):
        wizard = self.env["crm.salesperson.planner.visit.close.wiz"].create(
            {
                "reason_id": self.close_reason.id,
            }
        )
        self.assertEqual(wizard.reschedule_model, "visit")

    def test_default_reschedule_model_multicompany(self):
        company_2 = self.env["res.company"].create(
            {
                "name": "Test Reschedule Company",
                "salesperson_planner_reschedule_model": "visit",
            }
        )
        wizard_model = self.env["crm.salesperson.planner.visit.close.wiz"]
        wizard_company_1 = wizard_model.with_company(self.company).create(
            {
                "reason_id": self.close_reason.id,
            }
        )
        wizard_company_2 = wizard_model.with_company(company_2).create(
            {
                "reason_id": self.close_reason.id,
            }
        )
        self.assertEqual(wizard_company_1.reschedule_model, "visit")
        self.assertEqual(wizard_company_2.reschedule_model, "visit")

    def test_reschedule_visit(self):
        new_date = "2026-11-15"
        new_sequence = 30
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": True,
                    "reschedule_model": "visit",
                    "new_date": new_date,
                    "new_sequence": new_sequence,
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
        new_visit = self.env["crm.salesperson.planner.visit"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("id", "!=", self.visit.id),
                ("date", "=", new_date),
            ]
        )
        self.assertEqual(len(new_visit), 1)
        self.assertEqual(new_visit.state, "confirm")
        self.assertEqual(new_visit.sequence, new_sequence)
        self.assertEqual(new_visit.user_id, self.visit.user_id)
        self.assertEqual(new_visit.company_id, self.visit.company_id)
        self.assertTrue(new_visit.calendar_event_id)

    def test_close_visit_without_reschedule(self):
        Visit = self.env["crm.salesperson.planner.visit"]
        visits_before = Visit.search_count([])
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule": False,
                    "reschedule_model": "visit",
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
        self.assertEqual(Visit.search_count([]), visits_before)
