# Copyright 2024 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.crm.tests.common import TestCrmCommon

INCOMING_EMAIL = """Return-Path: {return_path}
X-Original-To: {to}
Delivered-To: {to}
Received: by mail.my.com (Postfix, from userid xxx)
    id 822ECBFB67; Mon, 24 Oct 2011 07:36:51 +0200 (CEST)
X-Spam-Checker-Version: SpamAssassin 3.3.1 (2010-03-16) on mail.my.com
X-Spam-Level:
X-Spam-Status: No, score=-1.0 required=5.0 tests=ALL_TRUSTED autolearn=ham
    version=3.3.1
Received: from [192.168.1.146]
    (Authenticated sender: {email_from})
    by mail.customer.com (Postfix) with ESMTPSA id 07A30BFAB4
    for <{to}>; Mon, 24 Oct 2011 07:36:50 +0200 (CEST)
Message-ID: {msg_id}
Date: Mon, 24 Oct 2011 11:06:29 +0530
From: {email_from}
User-Agent: Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.14)
    Gecko/20110223 Lightning/1.0b2 Thunderbird/3.1.8
MIME-Version: 1.0
To: {to}
Subject: {subject}
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 8bit

This is an example email. All sensitive content has been stripped out.

ALL GLORY TO THE HYPNOTOAD!

Cheers,

Somebody."""


class TestCrmAssignProject(TestCrmCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_project_id = cls.env["project.project"].create(
            {"name": "Test Mail Project"}
        )
        cls.sales_team_1.write(
            {
                "automatic_project_assignation": True,
                "automatic_assignation_project_id": cls.test_project_id.id,
            }
        )

    def test_mail_crm_assign_project(self):
        new_lead = self.format_and_process(
            INCOMING_EMAIL,
            "unknown.sender@test.example.com",
            self.sales_team_1.alias_email,
            subject="Delivery cost inquiry",
            target_model="crm.lead",
        )
        self.assertEqual(new_lead.project_id.id, self.test_project_id.id)

    def test_mail_crm_no_assign_project(self):
        self.sales_team_1.write(
            {
                "automatic_project_assignation": False,
            }
        )
        new_lead = self.format_and_process(
            INCOMING_EMAIL,
            "unknown.sender@test.example.com",
            self.sales_team_1.alias_email,
            subject="Delivery cost inquiry",
            target_model="crm.lead",
        )
        self.assertEqual(new_lead.project_id.id, False)
