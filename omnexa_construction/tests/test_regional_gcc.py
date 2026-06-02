# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.regional_compliance.gcc_package import get_gcc_compliance_snapshot


class TestRegionalGCC(FrappeTestCase):
	def test_gcc_snapshot(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		out = get_gcc_compliance_snapshot(contract[0])
		self.assertEqual(out["package"], "GCC")
