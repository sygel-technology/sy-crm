# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCrmSalespersonPlannerExtendedPhonecallSummaryPredefined(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.visit = cls.env["crm.salesperson.planner.visit"].create(
            {
                "partner_id": cls.partner.id,
                "user_id": cls.env.user.id,
                "date": "2026-11-10",
            }
        )
        cls.close_reason = cls.env["crm.salesperson.planner.visit.close.reason"].create(
            {
                "name": "Test Close Reason",
                "close_type": "cancel",
            }
        )
        cls.phonecall_summary = cls.env["crm.phonecall.summary"].create(
            {
                "name": "Test Phonecall Summary",
            }
        )

    def test_prepare_phonecall_with_predefined_summary(self):
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule_model": "phonecall",
                    "phonecall_summary_id": self.phonecall_summary.id,
                }
            )
        )
        vals = wizard._prepare_reschedule_phonecall_vals(self.visit)
        self.assertEqual(
            vals["summary_id"],
            self.phonecall_summary.id,
        )
        self.assertNotIn("name", vals)

    def test_create_phonecall_with_predefined_summary(self):
        wizard = (
            self.env["crm.salesperson.planner.visit.close.wiz"]
            .with_context(active_id=self.visit.id)
            .create(
                {
                    "reason_id": self.close_reason.id,
                    "reschedule_model": "phonecall",
                    "phonecall_summary_id": self.phonecall_summary.id,
                }
            )
        )
        wizard._action_reschedule_phonecall(self.visit)
        phonecall = self.env["crm.phonecall"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("summary_id", "=", self.phonecall_summary.id),
            ]
        )
        self.assertEqual(len(phonecall), 1)
        self.assertEqual(
            phonecall.summary_id,
            self.phonecall_summary,
        )
        self.assertEqual(
            phonecall.name,
            self.phonecall_summary.name,
        )
