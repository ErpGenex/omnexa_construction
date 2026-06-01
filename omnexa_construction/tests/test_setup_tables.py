# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.setup_tables import save_wizard_phases
from omnexa_construction.wizard.wizard_api import create_setup, save_wizard_step


class TestSetupTables(FrappeTestCase):
	def test_save_phases(self):
		company = frappe.db.get_value("Company", {}, "name")
		branch = frappe.db.get_value("Branch", {"company": company}, "name")
		if not company or not branch:
			self.skipTest("No company/branch")
		name = create_setup(company=company, branch=branch)["name"]
		save_wizard_step(name, 2, {"building_type": "mall"})
		result = save_wizard_phases(
			name,
			[
				{
					"phase_code": "PH-01",
					"phase_name": "Structure",
					"planned_finish": "2026-12-31",
					"weight_percent": 60,
				},
				{
					"phase_code": "PH-02",
					"phase_name": "Finishing",
					"planned_finish": "2027-06-30",
					"weight_percent": 40,
				},
			],
		)
		self.assertEqual(len(result["phases"]), 2)
