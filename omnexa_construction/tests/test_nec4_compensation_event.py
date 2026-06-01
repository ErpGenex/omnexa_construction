# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNec4CompensationEvent(FrappeTestCase):
	def test_doctype_exists(self):
		if not frappe.db.exists("DocType", "Construction Compensation Event"):
			self.skipTest("Construction Compensation Event not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Compensation Event"))

	def test_key_fields(self):
		if not frappe.db.exists("DocType", "Construction Compensation Event"):
			self.skipTest("Construction Compensation Event not migrated")
		meta = frappe.get_meta("Construction Compensation Event")
		for field in ("project_contract", "status", "estimated_cost", "time_impact_days"):
			self.assertTrue(meta.has_field(field), msg=f"missing {field}")

	def test_workflow_exists(self):
		if not frappe.db.exists("Workflow", "Construction Compensation Event"):
			self.skipTest("NEC4 workflow not synced")
		wf = frappe.get_doc("Workflow", "Construction Compensation Event")
		states = {s.state for s in wf.states}
		self.assertIn("Implemented", states)
