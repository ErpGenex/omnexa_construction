# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.fidic_compliance import compute_notice_due_date, time_bar_days_for_contract


class TestConstructionRfi(FrappeTestCase):
	def test_time_bar_days_default_without_contract(self):
		self.assertEqual(time_bar_days_for_contract("__missing__"), 28)

	def test_notice_due_date_computed(self):
		due = compute_notice_due_date("2026-01-01", "__missing__")
		self.assertIsNotNone(due)
