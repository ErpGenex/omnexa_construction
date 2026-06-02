# Copyright (c) 2026, Omnexa — World Class E2E smoke
import frappe
from frappe.tests.utils import FrappeTestCase

class TestWorldClassE2ESmoke(FrappeTestCase):
	def test_app_import(self):
		import omnexa_construction  # noqa: F401
		self.assertTrue(True)
