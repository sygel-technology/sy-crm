# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.crm.tests.common import TestCrmCommon


class TestTransferClientPortfolio(TestCrmCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.adm_user = cls.env.ref("base.user_admin")
        cls.demo_user = cls.env.ref("base.user_demo")
        (cls.demo_user | cls.adm_user).write(
            {"groups_id": [(4, cls.env.ref("sales_team.group_sale_manager").id)]}
        )
        cls.company_id = cls.env.company

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test",
                "email": cls.test_email_data[0],
                "is_company": True,
                "street": "123 Backer Street",
                "city": "london",
                "country_id": cls.env.ref("base.us").id,
                "zip": "12345",
                "user_id": cls.demo_user.id,
            }
        )

        cls.lead = (
            cls.env["crm.lead"]
            .with_user(cls.demo_user)
            .create(
                {
                    "name": "Nibbler Spacecraft Request",
                    "type": "lead",
                    "user_id": cls.demo_user.id,
                    "partner_id": cls.partner.id,
                    "contact_name": "Amy Wong",
                    "email_from": "amy.wong@test.example.com",
                    "country_id": cls.env.ref("base.us").id,
                    "probability": 20,
                }
            )
        )

        cls.activity_type = cls.env["mail.activity.type"].create(
            {
                "name": "Call for Demo",
                "delay_count": 6,
                "summary": "ACT 2 : I want to show you my ERP !",
                "res_model": "crm.lead",
            }
        )
        cls.opor_activity = cls.env["mail.activity"].create(
            {
                "activity_type_id": cls.activity_type.id,
                "note": "Content of the activity to log oports",
                "res_id": cls.lead.id,
                "res_model_id": cls.env.ref("crm.model_crm_lead").id,
                "user_id": cls.demo_user.id,
            }
        )
        cls.partner_activity = cls.env["mail.activity"].create(
            {
                "activity_type_id": cls.activity_type.id,
                "note": "Content of the activity to log partners",
                "res_id": cls.partner.id,
                "res_model_id": cls.env.ref("base.model_res_partner").id,
                "user_id": cls.demo_user.id,
            }
        )

    def _execute_transfer(self, context):
        transfer = (
            self.env["transfer.portfolio.wizard"]
            .with_context(**context)
            .create(context)
        )
        transfer.transfer_portfolio()

    def test_transfer_client_portfolio(self):
        self._execute_transfer(
            {
                "current_salesperson": self.demo_user.id,
                "new_salesperson": self.adm_user.id,
                "review_state": True,
                "contact_ids": self.partner.ids,
                "activity_ids": [self.opor_activity.id, self.partner_activity.id],
                "opportunity_ids": [self.lead.id],
                "is_server_action": True,
                "server_action_type": "lead",
                "update_salesperson_contact": True,
                "transfer_activities": True,
            }
        )

        self.assertEqual(self.partner.user_id.id, self.adm_user.id)
        self.assertEqual(self.lead.user_id.id, self.adm_user.id)
        self.assertEqual(self.opor_activity.user_id.id, self.adm_user.id)
        self.assertEqual(self.partner_activity.user_id.id, self.adm_user.id)

        self._execute_transfer(
            {
                "current_salesperson": self.adm_user.id,
                "new_salesperson": self.demo_user.id,
                "update_salesperson_contact": False,
                "contact_ids": self.partner.ids,
                "activity_ids": [self.opor_activity.id, self.partner_activity.id],
                "opportunity_ids": [self.lead.id],
                "transfer_activities": True,
            }
        )

        self.assertEqual(self.partner.user_id.id, self.adm_user.id)
        self.assertEqual(self.lead.user_id.id, self.demo_user.id)
        self.assertEqual(self.opor_activity.user_id.id, self.demo_user.id)
        self.assertEqual(self.partner_activity.user_id.id, self.adm_user.id)

        self.partner.write({"user_id": self.demo_user.id})
        self.lead.write({"user_id": self.demo_user.id})
        self.opor_activity.write({"user_id": self.demo_user.id})
        self.partner_activity.write({"user_id": self.demo_user.id})

        self.assertEqual(self.partner.user_id.id, self.demo_user.id)
        self.assertEqual(self.lead.user_id.id, self.demo_user.id)
        self.assertEqual(self.opor_activity.user_id.id, self.demo_user.id)
        self.assertEqual(self.partner_activity.user_id.id, self.demo_user.id)

        self._execute_transfer(
            {
                "current_salesperson": self.demo_user.id,
                "new_salesperson": self.adm_user.id,
                "contact_ids": self.partner.ids,
                "activity_ids": [self.opor_activity.id, self.partner_activity.id],
                "opportunity_ids": [self.lead.id],
                "transfer_activities": False,
            }
        )

        self.assertEqual(self.partner.user_id.id, self.adm_user.id)
        self.assertEqual(self.lead.user_id.id, self.adm_user.id)
        self.assertEqual(self.opor_activity.user_id.id, self.demo_user.id)
        self.assertEqual(self.partner_activity.user_id.id, self.demo_user.id)

    def test_not_transferable_filtered_in_wizard(self):
        stage_transfer = self.env["crm.stage"].create(
            {"name": "Transfer Stage", "allow_transfer_opportunity": True}
        )
        stage_no_transfer = self.env["crm.stage"].create(
            {"name": "No Transfer Stage", "allow_transfer_opportunity": False}
        )
        lead_transferable = self.env["crm.lead"].create(
            {
                "name": "Lead Transferable",
                "user_id": self.demo_user.id,
                "stage_id": stage_transfer.id,
            }
        )
        lead_not_transferable = self.env["crm.lead"].create(
            {
                "name": "Lead Not Transferable",
                "user_id": self.demo_user.id,
                "stage_id": stage_no_transfer.id,
            }
        )
        context = {
            "is_lead_server_action": True,
            "active_ids": [lead_transferable.id, lead_not_transferable.id],
        }
        wizard = (
            self.env["transfer.portfolio.wizard"].with_context(**context).create({})
        )
        self.assertIn(lead_transferable, wizard.opportunity_ids)
        self.assertNotIn(lead_not_transferable, wizard.opportunity_ids)
