#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.exceptions import ValidationError

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.sale_import_base.tests.common_sale_order_import import SaleImportCase


class TestSaleOrderImport(SaleImportCase):
    @property
    def payload_multi_sale(self):
        result = [self.chunk_vals["data_str"], self.chunk_vals["data_str"]]
        result[1]["payment"]["reference"] = "PMT-EXAMPLE-002"
        return result

    def setUp(self):
        super().setUp()
        self.api_key = "ASecureKeyEbay"
        collection = _PseudoCollection("sale.import.rest.services", self.env)
        self.sale_import_service_env = WorkContext(
            model_name="sale.order", collection=collection
        )

    def test_chunks_created(self):
        chunk_count_initial = self.env["queue.job.chunk"].search_count([])
        import_service = self.sale_import_service_env.component(usage="import")
        import_service.create(self.api_key, self.payload_multi_sale)
        chunk_count_after = self.env["queue.job.chunk"].search_count([])
        self.assertEqual(chunk_count_initial + 2, chunk_count_after)

    def test_wrong_key(self):
        import_service = self.sale_import_service_env.component(usage="import")
        with self.assertRaises(ValidationError):
            import_service.create("aWrongKey", self.payload_multi_sale)

    def test_key_not_mapped_to_channel(self):
        new_key = self.env["auth.api.key"].create(
            {"name": "aName", "key": "aKey", "user_id": 1}
        )
        import_service = self.sale_import_service_env.component(usage="import")
        with self.assertRaises(ValidationError):
            import_service.create(new_key.key, self.payload_multi_sale)
