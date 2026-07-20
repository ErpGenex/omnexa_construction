# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEnvironmentalRegister(FrappeTestCase):
	def test_environmental_aspect_doctype(self):
		if not frappe.db.exists("DocType", "Construction Environmental Aspect"):
			self.skipTest("Environmental doctypes not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Environmental Aspect"))

	def test_waste_log_doctype(self):
		if not frappe.db.exists("DocType", "Construction Waste Log"):
			self.skipTest("Environmental doctypes not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Waste Log"))

	def test_monitoring_doctype(self):
		if not frappe.db.exists("DocType", "Construction Environmental Monitoring"):
			self.skipTest("Environmental monitoring not migrated")
		self.assertTrue(frappe.db.exists("DocType", "Construction Environmental Monitoring"))

	def test_aspect_key_fields(self):
		if not frappe.db.exists("DocType", "Construction Environmental Aspect"):
			self.skipTest("Environmental doctypes not migrated")
		meta = frappe.get_meta("Construction Environmental Aspect")
		for field in ("project_contract", "aspect_type", "activity"):
			self.assertTrue(meta.has_field(field), msg=f"missing {field}")
