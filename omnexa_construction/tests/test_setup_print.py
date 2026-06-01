import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.construction_forms.setup_print import _branch_display_name, get_setup_print_context


class TestSetupPrint(FrappeTestCase):
	def test_branch_display_uses_branch_name_field(self):
		branch = frappe.db.get_value("Branch", {}, "name")
		if not branch:
			self.skipTest("No Branch on site")
		expected = frappe.db.get_value("Branch", branch, "branch_name")
		self.assertEqual(_branch_display_name(branch), expected)

	def test_setup_print_context_no_sql_error(self):
		setup = frappe.db.get_value("Construction Project Setup", {}, "name")
		if not setup:
			self.skipTest("No Construction Project Setup")
		doc = frappe.get_doc("Construction Project Setup", setup)
		ctx = get_setup_print_context(doc)
		self.assertIn("company_name", ctx)
		self.assertIn("branch_name", ctx)
