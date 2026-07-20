# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.bim_ifc_viewer import create_bim_issue_from_viewer, get_ifc_viewer_context


class TestBIMIFCViewer(FrappeTestCase):
	def test_get_ifc_viewer_context_empty(self):
		contract = self._ensure_contract()
		out = get_ifc_viewer_context(contract)
		self.assertEqual(out["project_contract"], contract)
		self.assertIsInstance(out["models"], list)

	def test_create_bim_issue_from_viewer(self):
		contract = self._ensure_contract()
		company, branch = frappe.db.get_value("Project Contract", contract, ["company", "branch"])
		model = frappe.get_doc(
			{
				"doctype": "Construction BIM Model Register",
				"project_contract": contract,
				"model_name": "Test IFC",
				"model_format": "IFC",
				"company": company,
				"branch": branch
	}
		).insert(ignore_permissions=True)
		out = create_bim_issue_from_viewer(contract, model.name, "Clash at Level 2")
		self.assertTrue(out.get("ok"))
		self.assertTrue(frappe.db.exists("Construction BIM Issue", out["name"]))

	def _ensure_contract(self):
		name = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not name:
			self.skipTest("No project contract")
		return name[0]
