# Copyright 2022 Ángel García de la Chica Herrera <angel.garcia@sygel.es>
# Copyright 2023 Pol López Montenegro <pol.lopez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TransferPorfolioWizard(models.TransientModel):
    _name = "transfer.portfolio.wizard"
    _description = "Transfer Portfolio Wizard"

    current_salesperson_id = fields.Many2one(
        comodel_name="res.users", string="Current Salesperson"
    )
    new_salesperson_id = fields.Many2one(
        comodel_name="res.users", string="New Salesperson"
    )
    review_state = fields.Boolean(default=False, string="Review States")
    contact_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Contacts",
        domain="[('user_id', '=', current_salesperson_id)]",
    )
    activity_ids = fields.Many2many(
        comodel_name="mail.activity",
        string="Opportunities Activities",
    )
    opportunity_ids = fields.Many2many(
        comodel_name="crm.lead",
        string="Opportunities",
        domain="[('user_id', '=', current_salesperson_id), "
        "('stage_id.allow_transfer_opportunity', '=', True)]",
    )
    is_server_action = fields.Boolean(default=False, string="Is server action")
    server_action_type = fields.Selection(
        selection=[("partner", "Partner"), ("lead", "Lead")],
        string="Server Action Types",
        default=False,
    )
    update_salesperson_contact = fields.Boolean(
        default=True, string="Update salesperson on contact"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    transfer_activities = fields.Boolean(
        string="Transfer Salesperson Activities",
        default=lambda self: self._default_transfer_activities(),
        readonly=False,
    )

    def _default_transfer_activities(self):
        context = self._context.copy()
        if "transfer_activities" in context:
            actual_state = context.get("transfer_activities", False)
        else:
            actual_state = self.env.company.transfer_activities
        return actual_state

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("is_lead_server_action"):
            opportunity_ids = self.env.context.get("active_ids")
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
                            self.env["crm.lead"]
                            .browse(opportunity_ids)
                            .mapped("partner_id")
                            .ids,
                        )
                    ],
                    "activity_ids": [
                        (
                            6,
                            0,
                            self.env["mail.activity"]
                            .search(
                                [
                                    "|",
                                    "&",
                                    ("res_model", "=", "crm.lead"),
                                    ("res_id", "in", opportunity_ids),
                                    "&",
                                    ("res_model", "=", "res.partner"),
                                    (
                                        "res_id",
                                        "in",
                                        self.env["crm.lead"]
                                        .browse(opportunity_ids)
                                        .mapped("partner_id")
                                        .ids,
                                    ),
                                ]
                            )
                            .ids,
                        )
                    ],
                }
            )
        elif self.env.context.get("is_partner_server_action"):
            partner_ids = self.env.context.get("active_ids")
            res.update(
                {
                    "is_server_action": True,
                    "server_action_type": "partner",
                    "review_state": True,
                    "contact_ids": [(6, 0, partner_ids)],
                    "opportunity_ids": [
                        (
                            6,
                            0,
                            self.env["res.partner"]
                            .browse(partner_ids)
                            .mapped("opportunity_ids")
                            .ids,
                        )
                    ],
                    "activity_ids": [
                        (
                            6,
                            0,
                            self.env["mail.activity"]
                            .search(
                                [
                                    "|",
                                    "&",
                                    ("res_model", "=", "crm.lead"),
                                    (
                                        "res_id",
                                        "in",
                                        self.env["res.partner"]
                                        .browse(partner_ids)
                                        .mapped("opportunity_ids")
                                        .ids,
                                    ),
                                    "&",
                                    ("res_model", "=", "res.partner"),
                                    ("res_id", "in", partner_ids),
                                ]
                            )
                            .ids,
                        )
                    ],
                }
            )
        return res

    def review_transfer(self):
        self.ensure_one()
        self.contact_ids = self.env["res.partner"].search(
            [("user_id", "=", self.current_salesperson_id.id)]
        )
        self.opportunity_ids = self.env["crm.lead"].search(
            [
                ("user_id", "=", self.current_salesperson_id.id),
                ("stage_id.allow_transfer_opportunity", "=", True),
            ]
        )
        self.activity_ids = self.env["mail.activity"].search(
            [
                "|",
                "&",
                ("res_model", "=", "crm.lead"),
                ("res_id", "in", self.opportunity_ids.ids),
                "&",
                ("res_model", "=", "res.partner"),
                ("res_id", "in", self.contact_ids.ids),
            ]
        )
        self.review_state = True
        return {
            "name": "Transfer Portfolio",
            "view_mode": "form",
            "view_id": False,
            "res_model": self._name,
            "domain": [],
            "context": dict(
                self._context,
                active_ids=self.ids,
                default_transfer_activities=self.transfer_activities,
            ),
            "type": "ir.actions.act_window",
            "target": "new",
            "res_id": self.id,
        }

    def clear_activity_ids(self):
        self.write({"activity_ids": [(5,)]})
        return True

    def transfer_portfolio(self):
        if not self.transfer_activities:
            self.clear_activity_ids()

        if not self.new_salesperson_id:
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
        if self.is_server_action:
            self.transfer_portfolio_server_action()
        else:
            self.transfer_portfolio_not_server_action(transfer_ids)

    def transfer_portfolio_not_server_action(self, transfer_ids):
        for sel in transfer_ids:
            vals = sel._get_vals_transfer_registry()
            self.env["portfolio.transfer.registry"].create(vals)
            self.env["res.partner"].browse(sel.contact_ids.ids).write(
                {
                    "previous_salesperson_id": sel.current_salesperson_id.id,
                    "user_id": sel.new_salesperson_id.id,
                }
            )
            self.env["crm.lead"].browse(sel.opportunity_ids.ids).write(
                {
                    "previous_salesperson_id": sel.current_salesperson_id.id,
                    "user_id": sel.new_salesperson_id.id,
                }
            )
            if sel.transfer_activities:
                oa_activities = sel.activity_ids.filtered(
                    lambda x: x.res_model == "crm.lead"
                ).ids
                self.env["mail.activity"].browse(oa_activities).write(
                    {
                        "previous_salesperson_id": sel.current_salesperson_id.id,
                        "user_id": sel.new_salesperson_id.id,
                    }
                )
            if sel.transfer_activities and sel.update_salesperson_contact:
                pa_activities = sel.activity_ids.filtered(
                    lambda x: x.res_model == "res.partner"
                ).ids
                self.env["mail.activity"].browse(pa_activities).write(
                    {
                        "previous_salesperson_id": sel.current_salesperson_id.id,
                        "user_id": sel.new_salesperson_id.id,
                    }
                )

    def transfer_portfolio_server_action(self):
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
        if self.transfer_activities:
            activities_grouped = self.env["mail.activity"].search(
                [
                    "|",
                    "&",
                    ("res_model", "=", "crm.lead"),
                    ("res_id", "in", self.opportunity_ids.ids),
                    "&",
                    ("res_model", "=", "res.partner"),
                    ("res_id", "in", self.contact_ids.ids),
                ]
            )
        records_by_salesperson = {}
        for o in opportunities_grouped:
            user_id = o.get("user_id")[0] if bool(o.get("user_id")) else False
            records_by_salesperson[user_id] = {
                "opt": self.opportunity_ids.filtered(
                    lambda x, user_id=user_id: x.user_id.id == user_id
                ).ids,
                "contacts": [],
                "oppor_activities": [],
                "partner_activities": [],
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
                    "oppor_activities": [],
                    "partner_activities": [],
                }
        if self.transfer_activities:
            for oa in activities_grouped.filtered(
                lambda act: act.res_model == "crm.lead"
            ):
                user_id = oa.user_id.id
                oa_activities = self.activity_ids.filtered(
                    lambda x: x.res_model == "crm.lead"
                ).ids
                if user_id in records_by_salesperson:
                    records_by_salesperson[user_id].update(
                        {"oppor_activities": oa_activities}
                    )
                else:
                    records_by_salesperson[user_id] = {
                        "opt": [],
                        "contacts": [],
                        "oppor_activities": oa_activities,
                        "partner_activities": [],
                    }

            for pa in activities_grouped.filtered(
                lambda act: act.res_model == "res.partner"
            ):
                user_id = pa.user_id.id
                pa_activities = self.activity_ids.filtered(
                    lambda x: x.res_model == "res.partner"
                ).ids
                if user_id in records_by_salesperson:
                    records_by_salesperson[user_id].update(
                        {"partner_activities": pa_activities}
                    )
                else:
                    records_by_salesperson[user_id] = {
                        "opt": [],
                        "contacts": [],
                        "oppor_activities": [],
                        "partner_activities": pa_activities,
                    }

        ptr_vals = []
        for rbs in records_by_salesperson:
            ptr_vals.append(
                self._get_vals_transfer_registry(
                    {
                        "previous_salesperson_id": rbs,
                        "list_opportunity_ids": records_by_salesperson[rbs]["opt"],
                        "list_contacts_ids": records_by_salesperson[rbs]["contacts"],
                        "list_oport_activity_ids": records_by_salesperson[rbs][
                            "oppor_activities"
                        ],
                        "list_partner_activity_ids": records_by_salesperson[rbs][
                            "partner_activities"
                        ],
                    }
                )
            )
            self.env["crm.lead"].browse(records_by_salesperson[rbs]["opt"]).write(
                {
                    "previous_salesperson_id": rbs,
                    "user_id": self.new_salesperson_id.id,
                }
            )
            self.env["res.partner"].browse(
                records_by_salesperson[rbs]["contacts"]
            ).write(
                {
                    "previous_salesperson_id": rbs,
                    "user_id": self.new_salesperson_id.id,
                }
            )

            if self.transfer_activities:
                self.env["mail.activity"].browse(
                    records_by_salesperson[rbs]["oppor_activities"]
                ).write(
                    {
                        "previous_salesperson_id": rbs,
                        "user_id": self.new_salesperson_id.id,
                    }
                )

            if self.transfer_activities and self.update_salesperson_contact:
                self.env["mail.activity"].browse(
                    records_by_salesperson[rbs]["partner_activities"]
                ).write(
                    {
                        "previous_salesperson_id": rbs,
                        "user_id": self.new_salesperson_id.id,
                    }
                )

        self.env["portfolio.transfer.registry"].create(ptr_vals)

    def clear_records(self):
        self.write({"contact_ids": False, "opportunity_ids": False})
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

    def _get_vals_transfer_registry(self, vals_def=None):
        if vals_def is None:
            vals_def = {}
        vals_def = {
            "user_made_transfer_id": self.env.user.id,
            "date_transfer": datetime.now(),
            "previous_salesperson_id": vals_def.get(
                "previous_salesperson_id", self.current_salesperson_id.id
            ),
            "new_salesperson_id": vals_def.get(
                "new_salesperson_id", self.new_salesperson_id.id
            ),
            "list_contacts_ids": "{}".format(
                vals_def.get("list_contacts_ids", self.contact_ids.ids)
            ),
            "list_opportunity_ids": "{}".format(
                vals_def.get("list_opportunity_ids", self.opportunity_ids.ids)
            ),
            "list_oport_activity_ids": "{}".format(
                vals_def.get("oppor_activities", False)
            ),
            "list_partner_activity_ids": "{}".format(
                vals_def.get("partner_activities", False)
            ),
        }
        return vals_def
