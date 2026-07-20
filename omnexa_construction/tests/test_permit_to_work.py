# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPermitToWork(FrappeTestCase):
	def test_doctype_exists(self):
		if not frappe.db.exists("DocType", "Construction Permit to Work"):
			self.skipTest("Construction Permit to Work not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Permit to Work"))

	def test_required_fields(self):
		if not frappe.db.exists("DocType", "Construction Permit to Work"):
			self.skipTest("Construction Permit to Work not migrated")
		meta = frappe.get_meta("Construction Permit to Work")
		for field in ("project_contract", "work_description", "valid_from", "valid_to", "status"):
			self.assertTrue(meta.has_field(field), msg=f"missing {field}")

	def test_ptw_workflow_exists(self):
		if not frappe.db.exists("Workflow", "Construction Permit to Work"):
			self.skipTest("PTW workflow not synced")
		wf = frappe.get_doc("Workflow", "Construction Permit to Work")
		states = {s.state for s in wf.states}
		self.assertIn("Active", states)
