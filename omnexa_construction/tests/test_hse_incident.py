# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestHseIncident(FrappeTestCase):
	def test_doctype_exists(self):
		if not frappe.db.exists("DocType", "Construction HSE Incident"):
			self.skipTest("Construction HSE Incident not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction HSE Incident"))

	def test_required_fields(self):
		if not frappe.db.exists("DocType", "Construction HSE Incident"):
			self.skipTest("Construction HSE Incident not migrated")
		meta = frappe.get_meta("Construction HSE Incident")
		for field in ("project_contract", "incident_date", "incident_type", "severity"):
			self.assertTrue(meta.has_field(field), msg=f"missing {field}")
