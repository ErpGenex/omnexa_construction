# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import cint

from omnexa_construction.wizard.wizard_api import create_setup, save_wizard_step


class TestWizardConcurrentSave(FrappeTestCase):
	def test_rapid_save_steps_no_timestamp_error(self):
		if not frappe.db.exists("Company", {"name": ("!=", "")}):
			self.skipTest("No company")
		company = frappe.db.get_value("Company", {}, "name")
		branch = frappe.db.get_value("Branch", {"company": company}, "name")
		if not branch:
			self.skipTest("No branch")
		created = create_setup(company=company, branch=branch)
		name = created["name"]
		save_wizard_step(name, 2, {"building_type": "mall"})
		save_wizard_step(name, 3, {"plot_area_m2": 600, "gross_floor_area_m2": 450})
		save_wizard_step(name, 4, {"site_region": "EG-CAIRO"})
		doc = frappe.get_doc("Construction Project Setup", name)
		self.assertEqual(cint(doc.wizard_step), 4)
