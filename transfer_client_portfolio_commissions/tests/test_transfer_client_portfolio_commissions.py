# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.transfer_client_portfolio.tests.test_transfer_client_portfolio import (
    TestTransferClientPortfolio,
)


class TestTransferClientPortfolioCommissions(TestTransferClientPortfolio):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.adm_agents = cls.adm_user.agent_ids

    def test_transfer_client_portfolio_commissions(self):
        self._execute_transfer(
            {
                "current_salesperson": self.demo_user.id,
                "new_salesperson": self.adm_user.id,
                "review_state": True,
                "contact_ids": self.partner.ids,
                "opportunity_ids": [self.lead.id],
                "update_salesperson_contact": True,
                "transfer_agents": True,
                "agent_ids": self.adm_agents.ids,
            }
        )

        self.assertEqual(self.partner.user_id.id, self.adm_user.id)
        self.assertEqual(self.lead.user_id.id, self.adm_user.id)
        self.assertEqual(self.partner.agent_ids.ids, self.adm_agents.ids)
