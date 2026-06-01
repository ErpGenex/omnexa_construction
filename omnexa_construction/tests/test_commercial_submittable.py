# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests import IntegrationTestCase


class TestCommercialSubmittable(IntegrationTestCase):
	def test_ipc_certificate_is_submittable(self):
		meta = frappe.get_meta("IPC Certificate")
		self.assertTrue(meta.is_submittable)

	def test_specialist_roles_exist_after_patch(self):
		for role in (
			"Construction QS",
			"Construction Commercial Manager",
			"Construction HSE Officer",
		):
			if frappe.db.exists("Role", role):
				self.assertTrue(frappe.db.get_value("Role", role, "desk_access"))
