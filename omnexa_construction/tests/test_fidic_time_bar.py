# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests import IntegrationTestCase

from omnexa_construction.fidic_compliance import compute_notice_due_date, time_bar_days_for_contract


class TestFidicTimeBar(IntegrationTestCase):
	def test_default_time_bar_days(self):
		self.assertEqual(time_bar_days_for_contract(""), 28)

	def test_compute_notice_due_date(self):
		due = compute_notice_due_date("2026-01-01", "")
		self.assertIsNotNone(due)
