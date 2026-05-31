# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.scaling import build_drivers, resolve_quantity, unit_cost_with_quality
from omnexa_construction.wizard.template_loader import VILLA_LINES


class TestWizardScaling(FrappeTestCase):
	def test_gfa_driver(self):
		drivers = {
			"GFA": 450,
			"gross_floor_area_m2": 450,
			"PLOT": 600,
			"plot_area_m2": 600,
			"FLOORS": 2,
			"ROAD_M": 0,
		}
		line = next(r for r in VILLA_LINES if r["cost_code"] == "03.10")
		qty = resolve_quantity(line, drivers)
		self.assertEqual(qty, 450 * 0.42)

	def test_quality_multiplier(self):
		self.assertGreater(unit_cost_with_quality(100, "Premium"), 100)

	def test_build_drivers_from_dict(self):
		class Setup:
			gross_floor_area_m2 = 500
			plot_area_m2 = 700
			number_of_floors = 3
			unit_count = 2
			road_length_m = 1000
			pipe_network_km = 0
			basement_levels = 1

		d = build_drivers(Setup())
		self.assertEqual(d["GFA"], 500)
		self.assertEqual(d["ROAD_M"], 1000)
