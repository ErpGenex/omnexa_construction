import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.regional_fields import (
	apply_regional_fields,
	resolve_regional_cost_factor_name,
)


class TestRegionalFields(FrappeTestCase):
	def test_numeric_input_clears_link(self):
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"regional_cost_factor": "0"
	}
		)
		apply_regional_fields(setup, {"regional_cost_factor": "0", "site_region": ""
	})
		self.assertIsNone(setup.regional_cost_factor)

	def test_resolve_by_region_code(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		if not frappe.db.exists("Regional Cost Factor", {"region_code": "EG-CAIRO", "company": company
	}):
			self.skipTest("No EG-CAIRO regional factor seeded")
		name = resolve_regional_cost_factor_name(None, company=company, site_region="eg-cairo")
		self.assertTrue(name)
