# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCRMLeadAttachRelatedSaleorderReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create partner, lead and quotations"""
        super().setUpClass()
        cls.partner_id = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "vat": "ESF35999705",
            }
        )
        cls.lead_id = cls.env["crm.lead"].create(
            {
                "name": "Test Lead",
                "partner_id": cls.partner_id.id,
            }
        )
        cls.order_id1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_id.id,
                "opportunity_id": cls.lead_id.id,
            }
        )
        cls.order_id2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_id.id,
                "opportunity_id": cls.lead_id.id,
            }
        )

    def test_attachments(self):
        """Open a lead mail wizard
        Attach quotations with the new button
        Check if quotations are attached correctly
        """
        composer = (
            self.env["mail.compose.message"]
            .with_context(
                **{
                    "active_ids": self.lead_id.ids,
                }
            )
            .create(
                {
                    "composition_mode": "comment",
                    "model": "crm.lead",
                    "res_ids": self.lead_id.ids,
                }
            )
        )
        self.assertTrue(composer.check_add_sale_attachments)
        composer.calculate_sale_attachments()
        self.assertEqual(len(composer.attachment_ids), 2)
