# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.world_class_mock_audit import run_mock_audit


class TestWorldClassMockAudit(FrappeTestCase):
	def test_run_mock_audit(self):
		company = frappe.defaults.get_defaults().company
		out = run_mock_audit(company)
		self.assertIn("overall_score", out)
		self.assertGreater(len(out.get("domains") or []), 0)
