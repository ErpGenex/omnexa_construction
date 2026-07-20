import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.spec_defaults import apply_wizard_spec_defaults, base_spec_defaults


class TestWizardSpecDefaults(FrappeTestCase):
	def test_building_defaults_applied(self):
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"building_type": "residential_building",
				"plot_area_m2": 0,
				"gross_floor_area_m2": 0
	}
		)
		apply_wizard_spec_defaults(setup)
		self.assertGreater(setup.plot_area_m2, 0)
		self.assertGreater(setup.gross_floor_area_m2, 0)
		self.assertEqual(setup.quality_tier, "Standard")

	def test_pipeline_defaults(self):
		defaults = base_spec_defaults("water_network")
		self.assertIn("pipe_network_km", defaults)
		self.assertNotIn("plot_area_m2", defaults)
