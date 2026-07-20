# Copyright (c) 2026, Omnexa and contributors
"""End-to-end wizard: all steps through demo project bundle creation."""

from __future__ import annotations

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.project_bundle import create_project_bundle, preview_boq, suggest_assignments
from omnexa_construction.wizard.wizard_api import create_setup, save_wizard_step, select_building_type


class TestWizardE2EDemoProject(FrappeTestCase):
	def test_full_wizard_creates_demo_project(self):
		company = frappe.db.get_value("Company", {}, "name")
		branch = frappe.db.get_value("Branch", {"company": company}, "name") if company else None
		customer = frappe.db.get_value("Customer", {}, "name")
		if not company or not branch:
			self.skipTest("No company/branch")
		if not customer:
			self.skipTest("No customer")

		out = create_setup(company=company, branch=branch)
		setup_name = out["name"]

		save_wizard_step(
			setup_name,
			2,
			{
				"client": customer,
				"contract_title": "مشروع تجريبي - معالج الإنشاءات",
				"contract_type": "Turnkey (EPC)",
				"site_location": "القاهرة - موقع تجريبي",
			},
		)
		tpl = select_building_type(setup_name, "villa")
		self.assertEqual(tpl.get("boq_template"), "VILLA-TURNKEY-STD")

		save_wizard_step(
			setup_name,
			4,
			{
				"building_type": "villa",
				"quality_tier": "Standard",
				"gross_floor_area_m2": 450,
				"plot_area_m2": 600,
				"number_of_floors": 2,
				"basement_levels": 0,
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
				"liquidated_damages_per_day": 500,
				"liquidated_damages_cap_percent": 10,
			},
		)

		boq = preview_boq(setup_name, save=1)
		self.assertGreater(boq["line_count"], 0)

		setup = frappe.get_doc("Construction Project Setup", setup_name)
		self.assertGreater(len(setup.boq_lines), 0)
		self.assertGreater(len(setup.phases or []), 0)
		self.assertGreater(len(setup.ipc_plan or []), 0)

		save_wizard_step(setup_name, 6, {})
		save_wizard_step(setup_name, 7, {})
		save_wizard_step(setup_name, 8, {})

		suggest_assignments(setup_name, save=1)
		setup.reload()
		self.assertGreater(len(setup.assignments or []), 0)

		bundle = create_project_bundle(setup_name)
		self.assertTrue(bundle.get("project_contract"))

		setup.reload()
		self.assertEqual(setup.status, "Completed")
		self.assertEqual(setup.project_contract, bundle["project_contract"])

		boq_count = frappe.db.count("BOQ Item", {"project_contract": bundle["project_contract"]})
		self.assertGreater(boq_count, 0)

		frappe.db.set_value(
			"Construction Project Setup",
			setup_name,
			{"status": "Draft", "project_contract": None},
			update_modified=False,
		)
		frappe.delete_doc("Construction Project Setup", setup_name, force=1)
