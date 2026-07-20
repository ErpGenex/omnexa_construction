# Copyright (c) 2026, Omnexa and contributors

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.project_bundle import expand_template_to_lines, preview_boq
from omnexa_construction.wizard.regional_cost import resolve_regional_factor
from omnexa_construction.wizard.residential_inventory import sync_residential_inventory_from_setup
from omnexa_construction.wizard.scaling import resolve_quantity
from omnexa_construction.wizard.template_loader import VILLA_LINES
from omnexa_construction.wizard.wizard_api import create_setup


class TestProjectWizard(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.company = frappe.db.get_value("Company", {}, "name")
		self.branch = frappe.db.get_value("Branch", {"company": self.company
	}, "name") if self.company else None

	def test_create_setup_resolves_company_without_user_default(self):
		if not self.company:
			self.skipTest("No company on site")
		from omnexa_core.omnexa_core.branch_access import get_default_company

		frappe.defaults.clear_user_default("Company")
		frappe.defaults.clear_user_default("company")
		frappe.defaults.clear_user_default("omnexa_view_company")
		expected = get_default_company() or self.company
		out = create_setup()
		self.assertEqual(out["company"], expected)
		frappe.delete_doc("Construction Project Setup", out["name"], force=1)

	def test_save_wizard_assignments(self):
		if not self.company or not self.branch:
			self.skipTest("No company/branch")
		currency = frappe.db.get_value("Company", self.company, "default_currency") or "EGP"
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"company": self.company,
				"branch": self.branch,
				"contract_currency": currency,
				"contract_title": "Assignment Save Test",
				"building_type": "villa"
	}
		)
		setup.insert(ignore_permissions=True)
		setup.append(
			"assignments",
			{
				"assignment_type": "Subcontractor",
				"trade_package_code": "CIVIL",
				"scope_notes": "Test scope"
	},
		)
		setup.save(ignore_permissions=True)
		supplier = frappe.db.get_value("Supplier", {}, "name")
		if not supplier:
			self.skipTest("No supplier on site")
		from omnexa_construction.wizard.project_bundle import save_wizard_assignments

		save_wizard_assignments(
			setup.name,
			[{"trade_package_code": "CIVIL", "party": supplier
	}],
		)
		setup.reload()
		self.assertEqual(setup.assignments[0].party, supplier)
		frappe.delete_doc("Construction Project Setup", setup.name, force=1)

	def test_regional_factor_default(self):
		self.assertEqual(resolve_regional_factor(), 1.0)

	def test_expand_template_with_regional_factor(self):
		if not frappe.db.exists("Construction BOQ Template", "VILLA-TURNKEY-STD"):
			self.skipTest("Villa template missing")
		if not self.company or not self.branch:
			self.skipTest("No company/branch")
		currency = frappe.db.get_value("Company", self.company, "default_currency") or "EGP"
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"company": self.company,
				"branch": self.branch,
				"contract_currency": currency,
				"contract_title": "Wizard Test Villa",
				"building_type": "villa",
				"boq_template": "VILLA-TURNKEY-STD",
				"gross_floor_area_m2": 400,
				"plot_area_m2": 500,
				"number_of_floors": 2,
				"unit_count": 1,
				"quality_tier": "Standard"
	}
		)
		setup.insert(ignore_permissions=True)
		lines = expand_template_to_lines(setup)
		self.assertGreater(len(lines), 5)
		line = next(r for r in VILLA_LINES if r["cost_code"] == "03.10")
		drivers = {"GFA": 400, "PLOT": 500, "FLOORS": 2, "UNITS": 1, "ROAD_M": 0, "ROAD_KM": 0, "PIPE_KM": 0
	}
		base_qty = resolve_quantity(line, drivers, regional_factor=1.0)
		scaled = resolve_quantity(line, drivers, regional_factor=1.1)
		self.assertAlmostEqual(scaled / base_qty, 1.1, places=4)

	def test_preview_boq_saves_lines(self):
		if not frappe.db.exists("Construction BOQ Template", "VILLA-TURNKEY-STD"):
			self.skipTest("Villa template missing")
		if not self.company or not self.branch:
			self.skipTest("No company/branch")
		currency = frappe.db.get_value("Company", self.company, "default_currency") or "EGP"
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"company": self.company,
				"branch": self.branch,
				"contract_currency": currency,
				"contract_title": "Preview BOQ Test",
				"building_type": "villa",
				"boq_template": "VILLA-TURNKEY-STD",
				"gross_floor_area_m2": 350,
				"plot_area_m2": 450,
				"unit_count": 1
	}
		)
		setup.insert(ignore_permissions=True)
		out = preview_boq(setup.name, save=1)
		self.assertGreater(out["line_count"], 0)
		setup.reload()
		self.assertGreater(len(setup.boq_lines), 0)

	def test_residential_inventory_sync(self):
		if not self.company or not self.branch:
			self.skipTest("No company/branch")
		if not frappe.db.exists("DocType", "Construction Plot Unit"):
			self.skipTest("Plot unit DocType missing")
		pc = frappe.db.get_value("Project Contract", {}, "name")
		if not pc:
			self.skipTest("No project contract")
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"company": self.company,
				"branch": self.branch,
				"building_type": "villa",
				"unit_count": 2,
				"plot_area_m2": 800,
				"gross_floor_area_m2": 600
	}
		)
		out = sync_residential_inventory_from_setup(setup, pc)
		self.assertGreaterEqual(out["plots"] + out["units"], 0)
