# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestCrmSaleAutomaticQuotationWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["crm.sale.automatic.quotation.wizard"]
        cls.WizardLine = cls.env["crm.sale.automatic.quotation.wizard.line"]
        cls.Lead = cls.env["crm.lead"]
        cls.Partner = cls.env["res.partner"]
        cls.SaleOrderTemplate = cls.env["sale.order.template"]

        cls.partner = cls.Partner.create(
            {"name": "Test Partner", "email": "partner@test.com"}
        )
        cls.lead = cls.Lead.create({"name": "Lead Test", "partner_id": cls.partner.id})

        cls.template = cls.SaleOrderTemplate.create(
            {
                "name": "Valid Template",
                "crm_automatic_quotation": True,
            }
        )

        cls.wizard = cls.Wizard.create({})

    def test_create_failed_lead_lines(self):
        """Wizard should create failed lead line records"""
        lines = self.wizard._create_failed_lead_lines(self.lead, "Some error")
        self.assertEqual(lines.lead_id, self.lead)
        self.assertEqual(lines.error, "Some error")
        self.assertEqual(lines.wizard_id, self.wizard)

    def test_filter_leads_and_classify_errors_no_partner(self):
        """Lead without partner should be classified as failed"""
        lead = self.Lead.create({"name": "Lead without partner"})
        _, failed = self.wizard._filter_leads_and_classify_errors(lead)
        self.assertIn("does not have a partner", failed.error)

    def test_create_quotations_with_valid_template(self):
        """Wizard should create quotation when valid template exists"""
        failed_lines = self.wizard._create_quotations(self.lead)
        self.assertFalse(failed_lines, "No failures expected")
        self.assertTrue(self.lead.order_ids, "Quotation should be created")

    def test_action_accept_with_valid_lead(self):
        """action_accept should move wizard state to end if no failures"""
        wizard = self.Wizard.with_context(active_ids=[self.lead.id]).create({})
        action = wizard.action_accept()
        self.assertEqual(wizard.wizard_state, "end")
        self.assertEqual(action["res_model"], wizard._name)
        self.assertEqual(action["target"], "new")

    def test_action_accept_with_failed_lead(self):
        """action_accept should classify lead as failed if missing partner"""
        lead = self.Lead.create({"name": "Lead without partner"})
        wizard = self.Wizard.with_context(active_ids=[lead.id]).create({})
        wizard.action_accept()
        self.assertEqual(wizard.wizard_state, "review")
        self.assertTrue(wizard.failed_lead_line_ids)
