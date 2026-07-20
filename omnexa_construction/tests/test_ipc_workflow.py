# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestIpcWorkflow(FrappeTestCase):
	def test_ipc_workflow_states(self):
		if not frappe.db.exists("Workflow", "IPC Certificate Approval"):
			self.skipTest("IPC workflow not synced")
		wf = frappe.get_doc("Workflow", "IPC Certificate Approval")
		states = {s.state for s in wf.states}
		for expected in ("Draft", "QS Review", "Commercial Review", "PM Approval", "Certified", "Posted"):
			self.assertIn(expected, states)

	def test_ipc_workflow_transitions_to_certified(self):
		if not frappe.db.exists("Workflow", "IPC Certificate Approval"):
			self.skipTest("IPC workflow not synced")
		wf = frappe.get_doc("Workflow", "IPC Certificate Approval")
		targets = {t.next_state for t in wf.transitions}
		self.assertIn("Certified", targets)
