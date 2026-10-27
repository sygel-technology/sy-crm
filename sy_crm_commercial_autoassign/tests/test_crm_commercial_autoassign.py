# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestCrmCommercialAutoassign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.salesperson_1 = cls.env.ref("base.user_admin")
        cls.salesperson_2 = cls.env.ref("base.user_demo")
        cls.city_1 = cls.env["res.city"].create(
            {
                "name": "Barcelona",
                "country_id": cls.env.ref("base.es").id,
            }
        )
        cls.city_2 = cls.env["res.city"].create(
            {
                "name": "Madrid",
                "country_id": cls.env.ref("base.es").id,
            }
        )

        cls.zip_1 = cls.env["res.city.zip"].create(
            {
                "name": "08001",
                "city_id": cls.city_1.id,
            }
        )
        cls.zip_2 = cls.env["res.city.zip"].create(
            {
                "name": "28001",
                "city_id": cls.city_2.id,
            }
        )
        cls.assignment_1 = cls.env["crm.commercial.autoassign"].create(
            {
                "name": "Barcelona",
                "user_id": cls.salesperson_1.id,
                "zip_ids": [(6, 0, cls.zip_1.ids)],
                "company_id": cls.env.company.id,
            }
        )
        cls.assignment_2 = cls.env["crm.commercial.autoassign"].create(
            {
                "name": "Madrid",
                "user_id": cls.salesperson_2.id,
                "zip_ids": [(6, 0, cls.zip_2.ids)],
                "company_id": cls.env.company.id,
            }
        )

    def test_salesperson_assignment_on_create(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip": "08001",
            }
        )
        self.assertEqual(partner.user_id, self.salesperson_1)

    def test_salesperson_assignment_on_zip_change(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip": "08001",
            }
        )
        partner.zip = "28001"
        self.assertEqual(partner.user_id, self.salesperson_2)

    def test_keep_salesperson(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip": "08001",
                "keep_salesperson": True,
                "user_id": self.salesperson_2.id,
            }
        )
        self.assertEqual(partner.user_id, self.salesperson_2)

    def test_keep_salesperson_on_zip_change(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip": "08001",
            }
        )
        partner.keep_salesperson = True
        partner.zip = "28001"
        self.assertEqual(partner.user_id, self.salesperson_1)

    def test_salesperson_without_matching_zip(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "zip": "99999",
                "user_id": self.salesperson_2.id,
            }
        )
        self.assertEqual(partner.user_id, self.salesperson_2)

    def test_duplicate_zip_assignment(self):
        with self.assertRaises(ValidationError):
            self.env["crm.commercial.autoassign"].create(
                {
                    "name": "Duplicate Barcelona",
                    "user_id": self.salesperson_2.id,
                    "zip_ids": [(6, 0, self.zip_1.ids)],
                    "company_id": self.env.company.id,
                }
            )
