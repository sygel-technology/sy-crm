# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmSalespersonPlannerVisitCloseWiz(models.TransientModel):
    _inherit = "crm.salesperson.planner.visit.close.wiz"

    reschedule_model = fields.Selection(
        selection_add=[
            ("phonecall", "Phone Calls"),
        ],
        ondelete={"phonecall": "set default"},
    )
    phonecall_name = fields.Char(
        string="Call Summary",
    )
    # Use Datetime instead of the original new_date field to allow
    # selecting both the date and time of the phone call.
    phonecall_date = fields.Datetime(
        string="Call Date",
        default=fields.Datetime.now,
    )
    # Use Char to avoid HTML tags, as crm.phonecall.description is a Text field.
    phonecall_description = fields.Char(
        string="Call Description",
    )
    phonecall_opportunity_ids = fields.Many2many(
        comodel_name="crm.lead",
        string="Available Opportunities",
    )
    phonecall_opportunity_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Opportunity",
        domain="[('id', 'in', phonecall_opportunity_ids)]",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        visit = self.env["crm.salesperson.planner.visit"].browse(
            self.env.context.get("active_id")
        )
        if visit.exists():
            # Visits can have multiple opportunities, but crm.phonecall only
            # supports one. Allow selecting an opportunity from the visit.
            opportunities = visit.opportunity_ids
            if "phonecall_opportunity_ids" in fields_list:
                res["phonecall_opportunity_ids"] = [
                    fields.Command.set(opportunities.ids)
                ]
            if "phonecall_opportunity_id" in fields_list and len(opportunities) == 1:
                res["phonecall_opportunity_id"] = opportunities.id
        return res

    def _action_reschedule(self, visits):
        if self.reschedule_model == "phonecall":
            res = self._action_reschedule_phonecall(visits)
        else:
            res = super()._action_reschedule(visits)
        return res

    def _action_reschedule_phonecall(self, visits):
        self.ensure_one()
        for visit in visits:
            vals = self._prepare_reschedule_phonecall_vals(visit)
            self.env["crm.phonecall"].create(vals)

    def _prepare_reschedule_phonecall_vals(self, visit):
        self.ensure_one()
        opportunity = self.phonecall_opportunity_id
        if opportunity and opportunity not in visit.opportunity_ids:
            raise UserError(
                self.env._("The selected opportunity is not linked to the visit.")
            )
        description_parts = []
        if self.phonecall_description:
            description_parts.append(self.phonecall_description)
        if self.reason_id:
            description_parts.append(
                self.env._("Close Reason: %s") % self.reason_id.name
            )
        if self.notes:
            description_parts.append(self.env._("Close Notes: %s") % self.notes)
        return {
            "name": self.phonecall_name,
            "date": self.phonecall_date,
            "description": "\n\n".join(description_parts),
            "partner_id": visit.partner_id.id,
            "company_id": visit.company_id.id,
            "user_id": visit.user_id.id,
            "opportunity_id": opportunity.id,
            "team_id": opportunity.team_id.id,
        }
