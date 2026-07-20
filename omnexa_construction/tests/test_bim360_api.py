# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.integrations.bim360_api import list_bim360_projects, sync_bim_model_to_bim360


class TestBIM360API(FrappeTestCase):
	def test_list_projects_empty_without_config(self):
		self.assertEqual(list_bim360_projects(), [])

	def test_sync_requires_settings(self):
		model = self._ensure_model()
		with self.assertRaises(frappe.ValidationError):
			sync_bim_model_to_bim360(model)

	def _ensure_model(self):
		company = frappe.defaults.get_defaults().company
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No project contract")
		branch = frappe.db.get_value("Project Contract", contract[0], "branch")
		return frappe.get_doc(
			{
				"doctype": "Construction BIM Model Register",
				"project_contract": contract[0],
				"model_name": "BIM360 Test",
				"company": company,
				"branch": branch
	}
		).insert(ignore_permissions=True).name
