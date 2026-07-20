# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.construction_forms.ipc_print import currency_display_label, get_ipc_print_context


class TestIpcPrint(FrappeTestCase):
	def test_ipc_print_context_structure(self):
		pc = frappe.db.get_value("Project Contract", {}, "name")
		if not pc:
			self.skipTest("No project contract")
		company = frappe.db.get_value("Project Contract", pc, "company")
		branch = frappe.db.get_value("Project Contract", pc, "branch")
		ipc = frappe.get_doc(
			{
				"doctype": "IPC Certificate",
				"project_contract": pc,
				"company": company,
				"branch": branch,
				"ipc_date": "2026-05-30",
				"period_from": "2026-04-01",
				"period_to": "2026-04-30",
				"boq_completion_percent": 40,
				"gross_amount": 730000,
				"retention_deduction": 50000,
				"net_amount": 680000
	}
		)
		with patch.object(ipc, "boq_lines", []):
			ctx = get_ipc_print_context(ipc)
		self.assertIn("boq_rows", ctx)
		self.assertIn("totals", ctx)
		self.assertIn("summary", ctx)
		self.assertEqual(ctx["certificate_number"], ipc.name)
		self.assertEqual(ctx["summary"]["retention"], 50000)
		self.assertEqual(ctx["summary"]["net_due"], 680000)

	def test_currency_display_label(self):
		self.assertEqual(currency_display_label("EGP"), "ج.م")
		self.assertEqual(currency_display_label("USD"), "USD")
