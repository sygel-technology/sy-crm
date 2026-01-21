# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestCrmSaleAutomaticQuotationAsynchronousWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["crm.sale.automatic.quotation.wizard"]

        cls.template = cls.env["mail.template"].create(
            {
                "name": "Test Template",
                "email_from": "test@example.com",
                "subject": "Test",
                "body_html": "<p>Test</p>",
            }
        )
        cls.quote = cls.env["sale.order"].create(
            {
                "name": "Test Quote",
                "partner_id": cls.env.ref("base.res_partner_1").id,
            }
        )

    def test__send_mail_asynchronous(self):
        wizard = self.wizard_model.create({})
        with patch.object(
            type(wizard), "_delay_send_mail", return_value=True
        ) as mock_delay:
            with patch.object(type(wizard), "with_delay", return_value=wizard):
                wizard._send_mail(self.template, [self.quote.id])
                mock_delay.assert_called_once_with(self.template, [self.quote.id])

    def test__delay_send_mail(self):
        wizard = self.wizard_model.create({})
        with patch.object(type(wizard), "_send_mail", return_value=True) as mock_send:
            wizard._delay_send_mail(self.template, [self.quote.id])
            mock_send.assert_called_once_with(self.template, [self.quote.id])
