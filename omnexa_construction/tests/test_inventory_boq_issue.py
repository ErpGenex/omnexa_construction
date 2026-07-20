# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.inventory_hooks import _default_issue_warehouse, create_material_issue_from_boq


class TestInventoryBoqIssue(FrappeTestCase):
	def test_default_issue_warehouse_none_without_rows(self):
		with patch("omnexa_construction.inventory_hooks.frappe.get_all", return_value=[]):
			self.assertIsNone(_default_issue_warehouse("Test Co"))

	def test_create_rejects_group_boq(self):
		boq = frappe._dict(is_group=1, material_bom=[], company="Test Co", project_contract="CTR-1")
		with patch("omnexa_construction.inventory_hooks.frappe.db.exists", return_value=True):
			with patch("omnexa_construction.inventory_hooks.frappe.get_doc", return_value=boq):
				with self.assertRaises(frappe.ValidationError):
					create_material_issue_from_boq("BOQ-GROUP")

	def test_create_rejects_empty_materials(self):
		boq = frappe._dict(is_group=0, material_bom=[], company="Test Co", project_contract="CTR-1")
		with patch("omnexa_construction.inventory_hooks.frappe.db.exists", return_value=True):
			with patch("omnexa_construction.inventory_hooks.frappe.get_doc", return_value=boq):
				with self.assertRaises(frappe.ValidationError):
					create_material_issue_from_boq("BOQ-001")
