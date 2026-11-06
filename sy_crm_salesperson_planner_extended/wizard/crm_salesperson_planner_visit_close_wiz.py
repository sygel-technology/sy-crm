# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError


class CrmSalespersonPlannerVisitCloseWiz(models.TransientModel):
    _inherit = "crm.salesperson.planner.visit.close.wiz"

    reschedule_model = fields.Selection(
        selection=[
            ("visit", "Visits"),
        ],
        string="Reschedule To",
        default=lambda self: self.env.company.salesperson_planner_reschedule_model,
        required=True,
        help="Select the type of record to create when rescheduling the visit.",
    )

    def action_close_reason_apply(self):
        self.ensure_one()
        visits = self.env["crm.salesperson.planner.visit"].browse(
            self.env.context.get("active_id")
        )

        self._action_close_visit(visits)

        if self.allow_reschedule and self.reschedule:
            self._action_reschedule(visits)

        return {"type": "ir.actions.act_window_close"}

    def _action_close_visit(self, visits):
        visit_close_method_name = f"action_{self.reason_id.close_type}"

        if not hasattr(visits, visit_close_method_name):
            raise ValueError(self.env._("The close reason type haven't a function."))

        getattr(visits, visit_close_method_name)(self.reason_id, self.image, self.notes)

    def _action_reschedule(self, visits):
        if self.reschedule_model == "visit":
            visits.copy(
                {
                    "date": self.new_date,
                    "sequence": self.new_sequence,
                    "opportunity_ids": visits.opportunity_ids.ids,
                }
            ).action_confirm()
        else:
            raise UserError(
                self.env._("The selected reschedule model is not implemented.")
            )
