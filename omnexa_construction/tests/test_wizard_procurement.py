# Copyright (c) 2026, Omnexa and contributors

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.catalog_import import ensure_construction_uoms, import_material_catalog
from omnexa_construction.wizard.material_bom import material_row_uom
from omnexa_construction.wizard.material_catalog import full_catalog, item_code
from omnexa_construction.wizard.procurement_rfq import create_rfq_from_purchase_request, evaluate_rfq


class TestWizardProcurement(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.company = frappe.db.get_value("Company", {}, "name")

	def test_catalog_has_up_to_200_items(self):
		self.assertGreaterEqual(len(full_catalog()), 100)
		self.assertLessEqual(len(full_catalog()), 200)

	def test_import_material_catalog(self):
		if not self.company:
			self.skipTest("No company")
		out = import_material_catalog(self.company)
		self.assertGreater(out["total"], 50)
		code = item_code("MAT-RMX-C30")
		self.assertTrue(frappe.db.exists("Item", {"item_code": code, "company": self.company}))

	def test_material_bom_uom_maps_lump_sum_to_stock_uom(self):
		if not self.company:
			self.skipTest("No company")
		ensure_construction_uoms()
		import_material_catalog(self.company, limit=30)
		code = item_code("MAT-RMX-C30")
		if not frappe.db.exists("Item", code):
			self.skipTest("Catalog item missing")
		uom = material_row_uom(code, "ls")
		self.assertNotEqual(uom.lower(), "ls")
		self.assertTrue(frappe.db.exists("UOM", uom))

	def test_rfq_from_pr_if_pr_exists(self):
		if not self.company:
			self.skipTest("No company")
		pr = frappe.db.get_value(
			"Purchase Request",
			{"company": self.company},
			"name",
			order_by="creation desc",
		)
		if not pr or not frappe.db.exists("DocType", "Construction RFQ"):
			return
		rfq_name = create_rfq_from_purchase_request(pr, auto_quotes=1)
		self.assertTrue(frappe.db.exists("Construction RFQ", rfq_name))
		result = evaluate_rfq(rfq_name)
		self.assertIn("quotes", result)
