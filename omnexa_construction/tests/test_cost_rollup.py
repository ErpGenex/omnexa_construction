# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.cost_rollup import (
	boq_actual_cost_breakdown,
	recompute_boq_actual_cost,
	site_material_cost_total,
)
from omnexa_construction.site_cost_rollup import recompute_boq_actual_cost_from_site_reports


class TestSiteCostRollup(FrappeTestCase):
	@patch("omnexa_construction.cost_rollup.frappe.db.sql", return_value=[[350.0]])
	def test_site_material_cost_total(self, _sql):
		self.assertEqual(site_material_cost_total("BOQ-1"), 350.0)

	@patch("omnexa_construction.cost_rollup.equipment_usage_cost_total", return_value=0.0)
	@patch("omnexa_construction.cost_rollup.timesheet_labor_cost_total", return_value=0.0)
	@patch("omnexa_construction.cost_rollup.site_material_cost_total", return_value=350.0)
	@patch("omnexa_construction.cost_rollup.frappe.db.exists", return_value=True)
	@patch("omnexa_construction.cost_rollup.frappe.db.set_value")
	def test_recompute_boq_actual_cost_from_site_reports(self, set_value, _exists, _mat, _lab, _eq):
		recompute_boq_actual_cost_from_site_reports("BOQ-1")
		set_value.assert_called_once_with("BOQ Item", "BOQ-1", "actual_cost", 350.0, update_modified=False)


class TestCostRollup(FrappeTestCase):
	@patch("omnexa_construction.cost_rollup.equipment_usage_cost_total", return_value=50.0)
	@patch("omnexa_construction.cost_rollup.timesheet_labor_cost_total", return_value=200.0)
	@patch("omnexa_construction.cost_rollup.site_material_cost_total", return_value=100.0)
	def test_boq_actual_cost_breakdown(self, _m, _l, _e):
		breakdown = boq_actual_cost_breakdown("BOQ-X")
		self.assertEqual(breakdown["material"], 100.0)
		self.assertEqual(breakdown["labor"], 200.0)
		self.assertEqual(breakdown["equipment"], 50.0)
		self.assertEqual(breakdown["total"], 350.0)

	@patch("omnexa_construction.cost_rollup.boq_actual_cost_breakdown", return_value={"total": 500.0})
	@patch("omnexa_construction.cost_rollup.frappe.db.exists", return_value=True)
	@patch("omnexa_construction.cost_rollup.frappe.db.set_value")
	def test_recompute_boq_actual_cost(self, set_value, _exists, _breakdown):
		total = recompute_boq_actual_cost("BOQ-9")
		self.assertEqual(total, 500.0)
		set_value.assert_called_once_with("BOQ Item", "BOQ-9", "actual_cost", 500.0, update_modified=False)
