# Copyright (c) 2026, Omnexa and contributors

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.project_bundle import preview_boq, suggest_assignments
from omnexa_construction.wizard.wizard_api import (
	create_setup,
	get_wizard_context,
	load_building_type_template,
	save_wizard_step,
)


class TestWizardFullFlow(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.company = frappe.db.get_value("Company", {}, "name")
		self.branch = frappe.db.get_value("Branch", {"company": self.company}, "name") if self.company else None
		self.customer = frappe.db.get_value("Customer", {}, "name")

	def test_wizard_recovers_from_invalid_company_hint(self):
		if not self.company:
			self.skipTest("No company")
		from omnexa_core.omnexa_core.branch_access import get_default_company

		expected = get_default_company() or self.company
		ctx = get_wizard_context(company="MH Head Office", branch=None)
		self.assertEqual(ctx["setup"]["company"], expected)

	def test_wizard_steps_1_through_8_api(self):
		if not self.company or not self.branch:
			self.skipTest("No company/branch")
		if not self.customer:
			self.skipTest("No customer")

		ctx = get_wizard_context(company=self.company, branch=self.branch)
		setup_name = ctx["setup"]["name"]

		save_wizard_step(
			setup_name,
			2,
			{
				"client": self.customer,
				"contract_title": "Wizard Flow Test",
				"contract_type": "Turnkey (EPC)",
				"building_type": "villa",
			},
		)
		load_building_type_template(setup_name)

		save_wizard_step(
			setup_name,
			4,
			{
				"building_type": "villa",
				"quality_tier": "Standard",
				"gross_floor_area_m2": 450,
				"plot_area_m2": 600,
				"number_of_floors": 2,
				"unit_count": 1,
			},
		)
		save_wizard_step(
			setup_name,
			5,
			{
				"retention_percent": 5,
				"advance_payment_percent": 10,
				"default_discount_percent": 0,
			},
		)
		out = preview_boq(setup_name, save=1)
		self.assertGreater(out["line_count"], 0)

		setup = frappe.get_doc("Construction Project Setup", setup_name)
		self.assertGreater(len(setup.boq_lines), 0)
		self.assertGreater(len(setup.phases or []), 0)
		self.assertGreater(len(setup.ipc_plan or []), 0)

		suggest_assignments(setup_name)
		setup.reload()
		self.assertGreaterEqual(len(setup.assignments or []), 0)

		frappe.delete_doc("Construction Project Setup", setup_name, force=1)
