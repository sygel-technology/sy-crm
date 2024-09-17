# Copyright 2023 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# Copyright 2023 Pol López Montenegro <pol.lopez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TransferPorfolioWizard(models.TransientModel):
    _inherit = "transfer.portfolio.wizard"

    transfer_agents = fields.Boolean(default=False)
    agent_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="res_partner_agents_rel",
        column1="agent_id",
        column2="res_partner_id",
        domain=[("agent", "=", True)],
        help="Select the agents to be transferred to the contacts. "
        "Leave the field empty to delete the current agents.",
        string="New Agents",
    )

    def transfer_portfolio(self):
        res = super().transfer_portfolio()
        transfer_ids = self.filtered(
            lambda x: (x.contact_ids or x.opportunity_ids) and x.transfer_agents
        )
        for sel in transfer_ids:
            if sel.transfer_agents:
                self.env["res.partner"].browse(sel.contact_ids.ids).write(
                    {"agent_ids": [(6, 0, sel.agent_ids.ids)]}
                )
        return res

    def _get_vals_transfer_registry(self, **vals_def):
        vals = super()._get_vals_transfer_registry(**vals_def)
        vals["list_agents_ids"] = f"{self.agent_ids.ids}"
        vals["transferred_agents"] = self.transfer_agents
        return vals
