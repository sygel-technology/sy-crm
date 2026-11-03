# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalespersonTransferPortfolioVisit(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.salesperson = cls.env["res.users"].create(
            {
                "name": "Previous Salesperson",
                "login": "previous_salesperson_visit",
            }
        )
        cls.new_salesperson = cls.env["res.users"].create(
            {
                "name": "New Salesperson",
                "login": "new_salesperson_visit",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "user_id": cls.salesperson.id,
            }
        )
        cls.stage = cls.env["crm.stage"].create(
            {
                "name": "Transferable Stage",
                "allow_transfer_opportunity": True,
            }
        )
        cls.opportunity = cls.env["crm.lead"].create(
            {
                "name": "Test Opportunity",
                "type": "opportunity",
                "partner_id": cls.partner.id,
                "user_id": cls.salesperson.id,
                "stage_id": cls.stage.id,
            }
        )

        visit_vals = {
            "partner_id": cls.partner.id,
            "opportunity_ids": [(6, 0, cls.opportunity.ids)],
            "user_id": cls.salesperson.id,
        }
        cls.visit_draft = cls.env["crm.salesperson.planner.visit"].create(
            {
                **visit_vals,
                "state": "draft",
            }
        )
        cls.visit_confirm = cls.env["crm.salesperson.planner.visit"].create(
            {
                **visit_vals,
                "state": "confirm",
            }
        )
        cls.visit_done = cls.env["crm.salesperson.planner.visit"].create(
            {
                **visit_vals,
                "state": "done",
            }
        )
        cls.visit_cancel = cls.env["crm.salesperson.planner.visit"].create(
            {
                **visit_vals,
                "state": "cancel",
            }
        )
        cls.visit_incident = cls.env["crm.salesperson.planner.visit"].create(
            {
                **visit_vals,
                "state": "incident",
            }
        )

    def test_review_transfer_visits(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        self.assertEqual(
            wizard.visit_ids,
            self.visit_draft | self.visit_confirm,
        )

    def test_transfer_portfolio_visits(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        wizard.transfer_portfolio()
        for visit in self.visit_draft | self.visit_confirm:
            self.assertEqual(visit.user_id, self.new_salesperson)
            self.assertEqual(
                visit.previous_salesperson_id,
                self.salesperson,
            )
        for visit in self.visit_done | self.visit_cancel | self.visit_incident:
            self.assertEqual(visit.user_id, self.salesperson)
            self.assertFalse(visit.previous_salesperson_id)

    def test_transfer_registry_visits(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        wizard.transfer_portfolio()
        registry = self.env["portfolio.transfer.registry"].search(
            [
                ("previous_salesperson_id", "=", self.salesperson.id),
                ("new_salesperson_id", "=", self.new_salesperson.id),
            ],
            order="id desc",
            limit=1,
        )
        self.assertTrue(registry)
        self.assertCountEqual(
            registry.list_visit_ids.strip("[]").replace(" ", "").split(","),
            [str(visit.id) for visit in self.visit_draft | self.visit_confirm],
        )

    def test_clear_records_visits(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        self.assertTrue(wizard.visit_ids)
        wizard.clear_records()
        self.assertFalse(wizard.visit_ids)

    def test_default_get_partner_server_action(self):
        wizard_model = self.env["transfer.portfolio.wizard"].with_context(
            active_ids=self.partner.ids,
            active_model="res.partner",
            is_partner_server_action=True,
        )
        wizard = wizard_model.create({})
        self.assertTrue(wizard.is_server_action)
        self.assertIn(self.partner, wizard.contact_ids)
        self.assertCountEqual(
            wizard.visit_ids.ids,
            (self.visit_draft | self.visit_confirm).ids,
        )

    def test_default_get_opportunity_server_action(self):
        wizard_model = self.env["transfer.portfolio.wizard"].with_context(
            active_ids=self.opportunity.ids,
            active_model="crm.lead",
            is_lead_server_action=True,
        )
        wizard = wizard_model.create({})
        self.assertTrue(wizard.is_server_action)
        self.assertIn(self.opportunity, wizard.opportunity_ids)
        self.assertCountEqual(
            wizard.visit_ids.ids,
            (self.visit_draft | self.visit_confirm).ids,
        )

    def test_transfer_visit_calendar_event(self):
        self.visit_confirm.create_calendar_event()
        event = self.visit_confirm.calendar_event_id
        self.assertTrue(event)
        self.assertEqual(event.user_id, self.salesperson)
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        wizard.transfer_portfolio()
        self.assertEqual(self.visit_confirm.user_id, self.new_salesperson)
        self.assertEqual(event.user_id, self.new_salesperson)

    def test_transfer_visit_different_salesperson(self):
        self.visit_draft.user_id = self.new_salesperson
        wizard = (
            self.env["transfer.portfolio.wizard"]
            .with_context(
                active_ids=self.partner.ids,
                active_model="res.partner",
                is_partner_server_action=True,
            )
            .create(
                {
                    "new_salesperson": self.salesperson.id,
                    "update_salesperson_contact": False,
                }
            )
        )
        wizard.visit_ids = self.visit_draft
        wizard.transfer_portfolio()
        self.assertEqual(self.visit_draft.user_id, self.salesperson)
        self.assertEqual(
            self.visit_draft.previous_salesperson_id,
            self.new_salesperson,
        )
        self.assertEqual(self.partner.user_id, self.salesperson)
