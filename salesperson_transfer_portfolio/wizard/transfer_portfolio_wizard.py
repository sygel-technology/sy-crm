# Copyright 2022 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# Copyright 2023 Pol López Montenegro <pol.lopez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TransferPorfolioWizard(models.TransientModel):
    _name = "transfer.portfolio.wizard"
    _description = "Transfer Portfolio Wizard"

    current_salesperson = fields.Many2one(comodel_name="res.users")
    new_salesperson = fields.Many2one(comodel_name="res.users")
    review_state = fields.Boolean(default=False)
    contact_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Contacts",
        domain="[('user_id', '=', current_salesperson)]",
    )
    opportunity_ids = fields.Many2many(
        comodel_name="crm.lead",
        string="Opportunities",
        domain="[('user_id', '=', current_salesperson),"
        "('stage_id.allow_transfer_opportunity', '=', True)]",
    )
    activity_ids = fields.Many2many(
        comodel_name="mail.activity",
        string="Opportunities Activities",
        domain="[('user_id', '=', current_salesperson)]",
    )
    is_server_action = fields.Boolean(default=False)
    server_action_type = fields.Selection(
        selection=[("partner", "Partner"), ("lead", "Lead")],
        default=False,
    )
    update_salesperson_contact = fields.Boolean(
        default=True, string="Update salesperson on contact"
    )
    transfer_activities = fields.Boolean(
        string="Transfer Salesperson Activities",
        default=lambda self: self._default_transfer_activities(),
    )

    def _default_transfer_activities(self):
        return self.env.company.transfer_activities

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("is_lead_server_action"):
            opportunity_ids = self.env.context.get("active_ids")
            contact_ids = (
                self.env["crm.lead"].browse(opportunity_ids).mapped("partner_id").ids
            )
            opportunity_ids = (
                self.env["crm.lead"]
                .browse(opportunity_ids)
                .filtered(lambda x: x.stage_id.allow_transfer_opportunity)
                .ids
            )
            activity_ids = (
                self.env["crm.lead"].browse(opportunity_ids).activity_ids
                | self.env["res.partner"].browse(contact_ids).activity_ids
            ).ids
            res.update(
                {
                    "is_server_action": True,
                    "server_action_type": "lead",
                    "review_state": True,
                    "opportunity_ids": [(6, 0, opportunity_ids)],
                    "contact_ids": [
                        (
                            6,
                            0,
                            contact_ids,
                        )
                    ],
                    "activity_ids": [(6, 0, activity_ids)],
                }
            )
        elif self.env.context.get("is_partner_server_action"):
            partner_ids = self.env.context.get("active_ids")
            opportunity_ids = (
                self.env["res.partner"]
                .browse(partner_ids)
                .mapped(
                    lambda p: p.opportunity_ids.filtered(
                        lambda x: x.stage_id.allow_transfer_opportunity
                    )
                )
                .ids
            )
            activity_ids = (
                self.env["crm.lead"].browse(opportunity_ids).activity_ids
                | self.env["res.partner"].browse(partner_ids).activity_ids
            ).ids
            res.update(
                {
                    "is_server_action": True,
                    "server_action_type": "partner",
                    "review_state": True,
                    "contact_ids": [(6, 0, partner_ids)],
                    "opportunity_ids": [(6, 0, opportunity_ids)],
                    "activity_ids": [(6, 0, activity_ids)],
                }
            )
        return res

    def review_transfer(self):
        self.ensure_one()
        self.contact_ids = self.env["res.partner"].search(
            [("user_id", "=", self.current_salesperson.id)]
        )
        self.opportunity_ids = self.env["crm.lead"].search(
            [
                ("user_id", "=", self.current_salesperson.id),
                ("stage_id.allow_transfer_opportunity", "=", True),
            ]
        )
        self.activity_ids = (
            self.opportunity_ids.activity_ids | self.contact_ids.activity_ids
        )
        self.review_state = True
        return {
            "name": "Transfer Portfolio",
            "view_mode": "form",
            "view_id": False,
            "res_model": self._name,
            "domain": [],
            "context": dict(self._context, active_ids=self.ids),
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    def transfer_portfolio(self):
        if not self.new_salesperson:
            raise ValidationError(_("You must select a new salesperson."))
        transfer_ids = self.filtered(lambda x: x.contact_ids or x.opportunity_ids)
        if not transfer_ids:
            raise ValidationError(_("There are no records to transfer."))
        if self.update_salesperson_contact:
            contact_child_ids = self.env["res.partner"].search(
                [("parent_id", "in", self.contact_ids.ids)]
            )
            self.contact_ids += contact_child_ids
        else:
            self.write({"contact_ids": False})
        if self.transfer_activities:
            if not self.update_salesperson_contact:
                self.activity_ids -= self.activity_ids.filtered(
                    lambda a: a.res_model == "res.partner"
                )
        else:
            self.write({"activity_ids": False})
        if self.is_server_action:
            opportunities_grouped = self.env["crm.lead"].read_group(
                domain=[("id", "in", self.opportunity_ids.ids)],
                fields=["id"],
                groupby=["user_id"],
                lazy=False,
            )
            partners_grouped = self.env["res.partner"].read_group(
                domain=[("id", "in", self.contact_ids.ids)],
                fields=["id"],
                groupby=["user_id"],
                lazy=False,
            )
            activities_grouped = self.env["mail.activity"].read_group(
                domain=[("id", "in", self.activity_ids.ids)],
                fields=["id"],
                groupby=["user_id"],
                lazy=False,
            )
            records_by_salesperson = {}
            for o in opportunities_grouped:
                user_id = o.get("user_id")[0] if bool(o.get("user_id")) else False
                records_by_salesperson[user_id] = {
                    "opt": self.opportunity_ids.filtered(
                        lambda x, user_id=user_id: x.user_id.id == user_id
                    ).ids,
                    "contacts": [],
                    "activities": [],
                }

            for p in partners_grouped:
                user_id = p.get("user_id")[0] if bool(p.get("user_id")) else False
                contacts = self.contact_ids.filtered(
                    lambda x, user_id=user_id: x.user_id.id == user_id
                ).ids
                if user_id in records_by_salesperson:
                    records_by_salesperson[user_id].update({"contacts": contacts})
                else:
                    records_by_salesperson[user_id] = {
                        "opt": [],
                        "contacts": contacts,
                        "activities": [],
                    }

            for a in activities_grouped:
                user_id = a.get("user_id")[0] if bool(a.get("user_id")) else False
                activities = self.activity_ids.filtered(
                    lambda x, user_id=user_id: x.user_id.id == user_id
                ).ids
                if user_id in records_by_salesperson:
                    records_by_salesperson[user_id].update({"activities": activities})
                else:
                    records_by_salesperson[user_id] = {
                        "opt": [],
                        "contacts": [],
                        "activities": activities,
                    }
            ptr_vals = []
            for rbs in records_by_salesperson:
                ptr_vals.append(
                    self._get_vals_transfer_registry(
                        **{
                            "previous_salesperson_id": rbs,
                            "list_opportunity_ids": records_by_salesperson[rbs]["opt"],
                            "list_contacts_ids": records_by_salesperson[rbs][
                                "contacts"
                            ],
                            "list_activity_ids": records_by_salesperson[rbs][
                                "activities"
                            ],
                        }
                    )
                )
                self.env["crm.lead"].browse(records_by_salesperson[rbs]["opt"]).write(
                    {"previous_salesperson_id": rbs, "user_id": self.new_salesperson.id}
                )
                self.env["res.partner"].browse(
                    records_by_salesperson[rbs]["contacts"]
                ).write(
                    {"previous_salesperson_id": rbs, "user_id": self.new_salesperson.id}
                )
                self.env["mail.activity"].browse(
                    records_by_salesperson[rbs]["activities"]
                ).write(
                    {"previous_salesperson_id": rbs, "user_id": self.new_salesperson.id}
                )
            self.env["portfolio.transfer.registry"].create(ptr_vals)
        else:
            for sel in transfer_ids:
                vals = sel._get_vals_transfer_registry()
                sel.env["portfolio.transfer.registry"].create(vals)
                self.env["res.partner"].browse(sel.contact_ids.ids).write(
                    {
                        "previous_salesperson_id": sel.current_salesperson.id,
                        "user_id": sel.new_salesperson.id,
                    }
                )
                self.env["crm.lead"].browse(sel.opportunity_ids.ids).write(
                    {
                        "previous_salesperson_id": sel.current_salesperson.id,
                        "user_id": sel.new_salesperson.id,
                    }
                )
                self.env["mail.activity"].browse(sel.activity_ids.ids).write(
                    {
                        "previous_salesperson_id": sel.current_salesperson.id,
                        "user_id": sel.new_salesperson.id,
                    }
                )

    def clear_records(self):
        self.write(
            {"contact_ids": False, "opportunity_ids": False, "activity_ids": False}
        )
        return {
            "name": "Transfer Portfolio",
            "view_mode": "form",
            "view_id": False,
            "res_model": self._name,
            "domain": [],
            "context": dict(self._context, active_ids=self.ids),
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    def _get_vals_transfer_registry(self, **vals_def):
        return {
            "user_made_transfer_id": self.env.user.id,
            "date_transfer": datetime.now(),
            "previous_salesperson_id": vals_def.get(
                "previous_salesperson_id", self.current_salesperson.id
            ),
            "new_salesperson_id": vals_def.get(
                "new_salesperson_id", self.new_salesperson.id
            ),
            "list_contacts_ids": "{}".format(
                vals_def.get("list_contacts_ids", self.contact_ids.ids)
            ),
            "list_opportunity_ids": "{}".format(
                vals_def.get("list_opportunity_ids", self.opportunity_ids.ids)
            ),
            "list_activity_ids": "{}".format(
                vals_def.get("list_activity_ids", self.activity_ids.ids)
            ),
        }
