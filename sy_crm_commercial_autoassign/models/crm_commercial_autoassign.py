# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrmCommercialAutoassign(models.Model):
    _name = "crm.commercial.autoassign"
    _description = "CRM Commercial Auto Assignment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesperson",
        required=True,
        tracking=True,
    )
    zip_ids = fields.Many2many(
        comodel_name="res.city.zip",
        string="ZIP Codes",
        tracking=True,
    )
    note = fields.Html(string="Notes")
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(default=True)

    @api.constrains("zip_ids", "company_id")
    def _check_zip_ids(self):
        for record in self:
            other_assignments = self.search(
                [
                    ("id", "!=", record.id),
                    ("company_id", "=", record.company_id.id),
                    ("zip_ids", "in", record.zip_ids.ids),
                ]
            )
            duplicated_zips = set(record.zip_ids.mapped("name")) & set(
                other_assignments.zip_ids.mapped("name")
            )
            if duplicated_zips:
                raise ValidationError(
                    _(
                        "The following ZIP codes are already assigned "
                        "to another salesperson in this company: %s"
                    )
                    % ", ".join(sorted(duplicated_zips))
                )
