# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCrmLead(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Partner = cls.env["res.partner"]
        cls.Lead = cls.env["crm.lead"]
        cls.SaleOrderTemplate = cls.env["sale.order.template"]

        cls.partner = cls.Partner.create(
            {"name": "Test Partner", "email": "test@example.com"}
        )
        cls.lead = cls.Lead.create(
            {
                "name": "Test Lead",
                "partner_id": cls.partner.id,
            }
        )

    def test_get_crm_automatic_quotation_values(self):
        """Ensure _get_crm_automatic_quotation_values returns expected dict"""
        template = self.SaleOrderTemplate.create(
            {
                "name": "Test Template",
                "crm_automatic_quotation": True,
            }
        )
        values = self.lead._get_crm_automatic_quotation_values(template)
        self.assertEqual(values["opportunity_id"], self.lead.id)
        self.assertEqual(values["partner_id"], self.partner.id)
        self.assertEqual(values["sale_order_template_id"], template.id)

    def test_action_generate_automatic_quotation_without_template(self):
        """Should raise ValidationError if no valid template is found"""
        with self.assertRaises(ValidationError):
            self.lead._action_generate_automatic_quotation()

    def test_action_generate_automatic_quotation_with_template(self):
        """Should create a quotation when a valid template exists"""
        template = self.SaleOrderTemplate.create(
            {
                "name": "Valid Template",
                "crm_automatic_quotation": True,
            }
        )
        quotation = self.lead._action_generate_automatic_quotation()
        self.assertTrue(quotation, "Quotation should be created")
        self.assertEqual(quotation.partner_id, self.partner)
        self.assertEqual(quotation.opportunity_id, self.lead)
        self.assertEqual(quotation.sale_order_template_id, template)

    def test_action_generate_automatic_quotation_from_wizard_flag(self):
        """
        Ensure domain excludes templates when
        cr_automatic_exclude_from_wizard=True
        """
        self.SaleOrderTemplate.create(
            {
                "name": "Excluded Template",
                "crm_automatic_quotation": True,
                "cr_automatic_exclude_from_wizard": True,
            }
        )
        with self.assertRaises(ValidationError):
            self.lead._action_generate_automatic_quotation(from_wizard=True)

    def test_action_open_crm_sale_automatic_quotation_wizard(self):
        """Should return a valid action dict to open the wizard"""
        action = self.lead.action_open_crm_sale_automatic_quotation_wizard()
        self.assertEqual(action["res_model"], "crm.sale.automatic.quotation.wizard")
        self.assertEqual(action["target"], "new")
        self.assertIn("active_ids", action["context"])
