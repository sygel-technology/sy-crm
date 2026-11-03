# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TransferPortfolioWizard(models.TransientModel):
    _inherit = "transfer.portfolio.wizard"

    phonecall_ids = fields.Many2many(
        comodel_name="crm.phonecall",
        string="Phone Calls",
        domain="[('state', 'in', ['open', 'pending'])]",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("is_partner_server_action") or self.env.context.get(
            "is_lead_server_action"
        ):
            partner_ids = res.get("contact_ids", [(6, 0, [])])[0][2]
            opportunity_ids = res.get("opportunity_ids", [(6, 0, [])])[0][2]

            phonecalls = self.env["crm.phonecall"].search(
                [
                    ("state", "in", ["open", "pending"]),
                    "|",
                    ("partner_id", "in", partner_ids),
                    ("opportunity_id", "in", opportunity_ids),
                ]
            )
            res["phonecall_ids"] = [(6, 0, phonecalls.ids)]
        return res

    def review_transfer(self):
        res = super().review_transfer()
        self.phonecall_ids = self.env["crm.phonecall"].search(
            [
                ("user_id", "=", self.current_salesperson.id),
                ("state", "in", ["open", "pending"]),
            ]
        )
        return res

    def clear_records(self):
        self.write({"phonecall_ids": False})
        return super().clear_records()

    def _get_phonecalls_to_transfer(self):
        self.ensure_one()
        phonecalls = self.phonecall_ids.filtered(
            lambda call: call.state in ("open", "pending")
        )
        if not self.is_server_action:
            phonecalls = phonecalls.filtered(
                lambda call: call.user_id == self.current_salesperson
            )
        return phonecalls

    def _get_vals_transfer_registry(self, **vals_def):
        vals = super()._get_vals_transfer_registry(**vals_def)
        phonecalls = self._get_phonecalls_to_transfer().filtered(
            lambda call: call.user_id.id == vals["previous_salesperson_id"]
        )
        vals["list_phonecall_ids"] = str(phonecalls.ids)
        return vals

    def transfer_portfolio(self):
        self.ensure_one()
        phonecalls = self._get_phonecalls_to_transfer()
        previous_salespersons = {call.id: call.user_id.id for call in phonecalls}
        res = super().transfer_portfolio()
        for call in phonecalls:
            call.write(
                {
                    "previous_salesperson_id": previous_salespersons[call.id],
                    "user_id": self.new_salesperson.id,
                }
            )
        return res
