# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.cde_workflow import validate_cde_status_transition


class TestCDEWorkflow(FrappeTestCase):
	def test_wip_to_shared_allowed(self):
		validate_cde_status_transition("WIP", "Shared")

	def test_published_to_wip_blocked(self):
		with self.assertRaises(frappe.ValidationError):
			validate_cde_status_transition("Published", "WIP")
