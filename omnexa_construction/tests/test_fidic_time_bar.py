# Copyright (c) 2026, Omnexa and contributors
# License: MIT

# flake-friendly: tests rely on frappe db for seeded clause references
import frappe

from frappe.tests.utils import FrappeTestCase

from frappe.utils import add_days, getdate

from omnexa_construction.fidic_compliance import (
	compute_notice_due_date,
	compute_notice_due_date_for_notice,
	time_bar_days_for_contract,
	time_bar_days_for_notice,
)


class TestFidicTimeBar(FrappeTestCase):
	def test_default_time_bar_days(self):
		self.assertEqual(time_bar_days_for_contract(""), 28)

	def test_compute_notice_due_date(self):
		due = compute_notice_due_date("2026-01-01", "")
		self.assertIsNotNone(due)

	def test_time_bar_days_uses_clause_reference(self):
		# Validate Phase 9.4: notice due date should follow clause reference time_bar_days
		ref_name = frappe.db.get_value(
			"Construction FIDIC Clause Reference",
			{"display_reference": "FIDIC 20.2.1 — Notice of Claim"},
			"name",
		)
		self.assertIsNotNone(ref_name)

		doc = {
			"fidic_clause_reference": ref_name,
			"project_contract": "",
			"notice_date": "2026-01-01",
		}
		self.assertEqual(time_bar_days_for_notice(doc), 28)

		due = compute_notice_due_date_for_notice(doc)
		self.assertEqual(str(due), str(add_days(getdate("2026-01-01"), 28)))
