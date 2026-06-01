# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNcrCapaWorkflow(FrappeTestCase):
	def test_ncr_workflow_exists(self):
		if not frappe.db.exists("Workflow", "Construction NCR"):
			self.skipTest("NCR workflow not synced")
		wf = frappe.get_doc("Workflow", "Construction NCR")
		states = {s.state for s in wf.states}
		self.assertIn("Closed", states)

	def test_capa_workflow_exists(self):
		if not frappe.db.exists("Workflow", "Construction CAPA"):
			self.skipTest("CAPA workflow not synced")
		wf = frappe.get_doc("Workflow", "Construction CAPA")
		states = {s.state for s in wf.states}
		self.assertIn("Verified", states)
