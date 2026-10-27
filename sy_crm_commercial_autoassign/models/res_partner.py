# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    keep_salesperson = fields.Boolean(
        help="If enabled, the salesperson will not be automatically reassigned "
        "when the partner's ZIP code changes.",
    )

    def _get_salesperson_by_zip(self, zip_code, company):
        salesperson = self.env["res.users"]
        if zip_code:
            assignment = self.env["crm.commercial.autoassign"].search(
                [
                    ("company_id", "=", company.id),
                    ("zip_ids.name", "=", zip_code),
                ],
                limit=1,
            )
            salesperson = assignment.user_id
        return salesperson

    def _update_salesperson_by_zip(self):
        for partner in self:
            if not partner.keep_salesperson:
                company = partner.company_id or self.env.company
                salesperson = self._get_salesperson_by_zip(partner.zip, company)
                if salesperson:
                    partner.user_id = salesperson

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._update_salesperson_by_zip()
        return partners

    def write(self, vals):
        result = super().write(vals)
        if {"zip", "company_id", "keep_salesperson"} & vals.keys():
            self._update_salesperson_by_zip()
        return result
