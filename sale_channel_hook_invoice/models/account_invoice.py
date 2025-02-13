#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

import base64
import logging

from odoo import models

FIELDS_SIMPLE_COPY = ["name", "amount_total_signed"]

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "sale.channel.hook.mixin"]

    def action_invoice_paid(self):
        result = super().action_invoice_paid()
        for rec in self:
            origin = rec.invoice_line_ids.mapped("sale_line_ids").mapped("order_id")
            if len(origin.ids) > 1:
                _logger.warning("Two possible SOs detected for invoice hook")
            if origin and origin[0].sale_channel_id.hook_active_create_invoice:
                rec.trigger_channel_hook("create_invoice", origin[0])
        return result

    def get_hook_content_create_invoice(self, origin):
        data = {"sale_name": origin.client_order_ref, "invoice": self.name}
        if self.sale_channel_id.hook_active_create_invoice_send_pdf:
            report = self.sale_channel_id.hook_active_create_invoice_report
            pdf_bin = report._render_qweb_pdf([self.id])[0]
            pdf_encoded = base64.b64encode(pdf_bin)
            data["pdf"] = pdf_encoded
        return {"name": "order_invoice", "data": data}
