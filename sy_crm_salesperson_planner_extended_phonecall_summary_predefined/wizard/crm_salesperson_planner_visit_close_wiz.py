# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class CrmSalespersonPlannerVisitCloseWiz(models.TransientModel):
    _inherit = "crm.salesperson.planner.visit.close.wiz"

    phonecall_summary_id = fields.Many2one(
        comodel_name="crm.phonecall.summary",
        string="Call Summary",
    )

    def _prepare_reschedule_phonecall_vals(self, visit):
        vals = super()._prepare_reschedule_phonecall_vals(visit)
        vals.pop("name", None)
        vals["summary_id"] = self.phonecall_summary_id.id
        return vals
