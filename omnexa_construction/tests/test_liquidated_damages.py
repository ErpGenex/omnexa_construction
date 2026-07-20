# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.liquidated_damages import calc_ld_amount, calc_delay_days


class TestLiquidatedDamages(FrappeTestCase):
	def test_calc_delay_days(self):
		self.assertEqual(calc_delay_days("2026-01-01", "2026-01-11"), 10)
		self.assertEqual(calc_delay_days("2026-01-10", "2026-01-01"), 0)

	def test_calc_ld_amount_cap(self):
		result = calc_ld_amount(
			"NONEXISTENT-CONTRACT",
			100,
			amount_override=50000,
		)
		self.assertEqual(result["delay_days"], 100)
		self.assertEqual(result["ld_amount"], 50000)
