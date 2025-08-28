# Copyright 2022 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    previous_salesperson_id = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        string="Previous Salesperson",
    )

    def transfer_portfolio_server_action(self):
        result_view = self.env.ref(
            "salesperson_transfer_portfolio.transfer_portfolio_wizard_form",
            raise_if_not_found=False,
        )
        ctx = {
            "active_ids": self.ids,
            "is_lead_server_action": True,
        }
        return {
            "name": _("Transfer Opportunities"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "transfer.portfolio.wizard",
            "views": [(result_view.id, "form")],
            "view_id": result_view.id,
            "target": "new",
            "context": ctx,
        }
