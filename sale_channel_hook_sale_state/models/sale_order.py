#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "sale.channel.hook.mixin"]

    def write(self, vals):
        result = super().write(vals)
        for rec in self:
            if ("state" in vals.keys()) and rec.sale_channel_id.hook_active_sale_state:
                rec.trigger_channel_hook("sale_state")
        return result

    def get_hook_content_sale_state(self, *args):
        data = {"sale_name": self.client_order_ref, "state": self.state}
        return {"name": "order_state", "data": data}
