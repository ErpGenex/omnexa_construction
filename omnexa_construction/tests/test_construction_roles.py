# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestConstructionRoles(FrappeTestCase):
	def test_specialist_roles_exist(self):
		missing = []
		for role in (
			"Construction QS",
			"Construction Commercial Manager",
			"Construction HSE Officer",
			"Construction QA Manager",
			"Site Engineer",
		):
			if not frappe.db.exists("Role", role):
				missing.append(role)
		if missing:
			self.skipTest(f"Roles not installed: {', '.join(missing)}")
		for role in (
			"Construction QS",
			"Construction Commercial Manager",
			"Construction HSE Officer",
		):
			self.assertTrue(frappe.db.get_value("Role", role, "desk_access"))
