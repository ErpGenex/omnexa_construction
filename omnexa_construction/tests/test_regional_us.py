# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.regional_compliance.us_package import export_certified_payroll, get_us_compliance_snapshot


class TestRegionalUS(FrappeTestCase):
	def test_us_snapshot(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		out = get_us_compliance_snapshot(contract[0])
		self.assertEqual(out["package"], "US")

	def test_payroll_export(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		out = export_certified_payroll(contract[0])
		self.assertIn("csv", out)
