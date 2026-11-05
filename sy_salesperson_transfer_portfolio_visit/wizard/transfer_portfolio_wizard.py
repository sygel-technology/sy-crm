# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TransferPortfolioWizard(models.TransientModel):
    _inherit = "transfer.portfolio.wizard"

    visit_ids = fields.Many2many(
        comodel_name="crm.salesperson.planner.visit",
        string="Visits",
        domain="[('state', 'in', ['draft', 'confirm'])]",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("is_partner_server_action") or self.env.context.get(
            "is_lead_server_action"
        ):
            partner_ids = res.get("contact_ids", [(6, 0, [])])[0][2]
            opportunity_ids = res.get("opportunity_ids", [(6, 0, [])])[0][2]
            visits = self.env["crm.salesperson.planner.visit"].search(
                [
                    ("state", "in", ["draft", "confirm"]),
                    "|",
                    ("partner_id", "in", partner_ids),
                    ("opportunity_ids", "in", opportunity_ids),
                ]
            )
            res["visit_ids"] = [(6, 0, visits.ids)]
        return res

    def review_transfer(self):
        res = super().review_transfer()
        self.visit_ids = self.env["crm.salesperson.planner.visit"].search(
            [
                ("user_id", "=", self.current_salesperson.id),
                ("state", "in", ["draft", "confirm"]),
            ]
        )
        return res

    def clear_records(self):
        self.write({"visit_ids": False})
        return super().clear_records()

    def _get_visits_to_transfer(self):
        self.ensure_one()
        visits = self.visit_ids.filtered(
            lambda visit: visit.state in ("draft", "confirm")
        )
        if not self.is_server_action:
            visits = visits.filtered(
                lambda visit: visit.user_id == self.current_salesperson
            )
        return visits

    def _get_vals_transfer_registry(self, **vals_def):
        vals = super()._get_vals_transfer_registry(**vals_def)
        visits = self._get_visits_to_transfer().filtered(
            lambda visit: visit.user_id.id == vals["previous_salesperson_id"]
        )
        vals["list_visit_ids"] = str(visits.ids)
        return vals

    def transfer_portfolio(self):
        self.ensure_one()
        visits = self._get_visits_to_transfer()
        previous_salespersons = {visit.id: visit.user_id.id for visit in visits}
        res = super().transfer_portfolio()
        for visit in visits:
            visit.write(
                {
                    "previous_salesperson_id": previous_salespersons[visit.id],
                    "user_id": self.new_salesperson.id,
                }
            )
        return res
