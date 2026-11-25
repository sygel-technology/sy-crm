# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalespersonTransferPortfolioPhonecall(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.salesperson = cls.env["res.users"].create(
            {
                "name": "Previous Salesperson",
                "login": "previous_salesperson_phonecall",
            }
        )
        cls.new_salesperson = cls.env["res.users"].create(
            {
                "name": "New Salesperson",
                "login": "new_salesperson_phonecall",
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
        cls.phonecall_open = cls._create_phonecall("Open Phone Call", "open")
        cls.phonecall_pending = cls._create_phonecall("Pending Phone Call", "pending")
        cls.phonecall_done = cls._create_phonecall("Done Phone Call", "done")
        cls.phonecall_cancel = cls._create_phonecall("Cancelled Phone Call", "cancel")

    @classmethod
    def _create_phonecall(cls, name, state):
        vals = {
            "name": name,
            "partner_id": cls.partner.id,
            "opportunity_id": cls.opportunity.id,
            "user_id": cls.salesperson.id,
            "state": state,
        }
        if "summary_id" in cls.env["crm.phonecall"]._fields:
            summary = cls.env["crm.phonecall.summary"].create({"name": name})
            vals["summary_id"] = summary.id
            vals.pop("name")
        return cls.env["crm.phonecall"].create(vals)

    def test_review_transfer_phonecalls(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        self.assertEqual(
            wizard.phonecall_ids,
            self.phonecall_open | self.phonecall_pending,
        )

    def test_transfer_portfolio_phonecalls(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        wizard.transfer_portfolio()
        for phonecall in self.phonecall_open | self.phonecall_pending:
            self.assertEqual(phonecall.user_id, self.new_salesperson)
            self.assertEqual(
                phonecall.previous_salesperson_id,
                self.salesperson,
            )
        for phonecall in self.phonecall_done | self.phonecall_cancel:
            self.assertEqual(phonecall.user_id, self.salesperson)
            self.assertFalse(phonecall.previous_salesperson_id)

    def test_transfer_registry_phonecalls(self):
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
            registry.list_phonecall_ids.strip("[]").replace(" ", "").split(","),
            [str(call.id) for call in self.phonecall_open | self.phonecall_pending],
        )

    def test_clear_records_phonecalls(self):
        wizard = self.env["transfer.portfolio.wizard"].create(
            {
                "current_salesperson": self.salesperson.id,
                "new_salesperson": self.new_salesperson.id,
            }
        )
        wizard.review_transfer()
        self.assertTrue(wizard.phonecall_ids)
        wizard.clear_records()
        self.assertFalse(wizard.phonecall_ids)

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
            wizard.phonecall_ids.ids,
            (self.phonecall_open | self.phonecall_pending).ids,
        )

    def test_transfer_phonecall_different_salesperson(self):
        self.phonecall_open.user_id = self.new_salesperson
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
        wizard.phonecall_ids = self.phonecall_open
        wizard.transfer_portfolio()
        self.assertEqual(self.phonecall_open.user_id, self.salesperson)
        self.assertEqual(
            self.phonecall_open.previous_salesperson_id,
            self.new_salesperson,
        )
        self.assertEqual(self.partner.user_id, self.salesperson)
