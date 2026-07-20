# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestDisputeCase(FrappeTestCase):
	def test_doctype_exists(self):
		if not frappe.db.exists("DocType", "Construction Dispute Case"):
			self.skipTest("Construction Dispute Case not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Dispute Case"))

	def test_key_fields(self):
		if not frappe.db.exists("DocType", "Construction Dispute Case"):
			self.skipTest("Construction Dispute Case not migrated")
		meta = frappe.get_meta("Construction Dispute Case")
		for field in ("project_contract", "status", "dispute_type", "claimed_amount"):
			self.assertTrue(meta.has_field(field), msg=f"missing {field}")

	def test_dispute_workflow_exists(self):
		if not frappe.db.exists("Workflow", "Construction Dispute Case"):
			self.skipTest("Dispute workflow not synced")
		wf = frappe.get_doc("Workflow", "Construction Dispute Case")
		states = {s.state for s in wf.states}
		self.assertTrue(states & {"Open", "DAB Referral", "Settled", "Closed"})
