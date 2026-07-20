# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.ipc_taxes import compute_ipc_tax_amounts


class TestIpcTaxes(FrappeTestCase):
	def test_vat_and_wht_net_after_tax(self):
		out = compute_ipc_tax_amounts(net_amount=100_000, gross_amount=120_000, vat_percent=14, wht_percent=5)
		self.assertAlmostEqual(out["vat_amount"], 16_800)
		self.assertAlmostEqual(out["wht_amount"], 5_000)
		self.assertAlmostEqual(out["net_after_tax"], 111_800)

	def test_zero_rates(self):
		out = compute_ipc_tax_amounts(net_amount=50_000, gross_amount=50_000)
		self.assertEqual(out["net_after_tax"], 50_000)
