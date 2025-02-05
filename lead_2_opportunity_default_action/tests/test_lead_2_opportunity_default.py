# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests.common import Form

from odoo.addons.crm.tests import common as crm_common


class TestLead2OpportunityDefault(crm_common.TestLeadConvertMassCommon):
    def test_lead_2_opportunity_partner_default(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "lead_2_opportunity_default_action.default", "convert"
        )
        lead = self.env["crm.lead"].browse(self.lead_1.ids)
        wizard = Form(
            self.env["crm.lead2opportunity.partner"].with_context(
                **{
                    "active_model": "crm.lead",
                    "active_id": lead.id,
                    "active_ids": lead.ids,
                }
            )
        )
        self.assertEqual(wizard.name, "convert")
        self.env["ir.config_parameter"].sudo().set_param(
            "lead_2_opportunity_default_action.default", "merge"
        )
        wizard = Form(
            self.env["crm.lead2opportunity.partner"].with_context(
                **{
                    "active_model": "crm.lead",
                    "active_id": lead.id,
                    "active_ids": lead.ids,
                }
            )
        )
        self.assertEqual(wizard.name, "merge")

    def test_lead_2_opportunity_mass_default(self):
        leads = self.lead_1 + self.lead_w_partner + self.lead_w_email_lost
        self.env["ir.config_parameter"].sudo().set_param(
            "lead_2_opportunity_default_action.default", "convert"
        )
        wizard = (
            self.env["crm.lead2opportunity.partner.mass"]
            .with_context(
                **{
                    "active_model": "crm.lead",
                    "active_ids": leads.ids,
                    "active_id": leads.ids[0],
                }
            )
            .create({})
        )
        self.assertEqual(wizard.name, "convert")

        self.env["ir.config_parameter"].sudo().set_param(
            "lead_2_opportunity_default_action.default", "merge"
        )
        wizard = (
            self.env["crm.lead2opportunity.partner.mass"]
            .with_context(
                **{
                    "active_model": "crm.lead",
                    "active_ids": leads.ids,
                    "active_id": leads.ids[0],
                }
            )
            .create({})
        )
        self.assertEqual(wizard.name, "merge")
