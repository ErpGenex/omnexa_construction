# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.evm_metrics import (
	earned_value_from_boq,
	planned_value,
	schedule_percent_planned,
)


class TestEVMMetrics(FrappeTestCase):
	def test_planned_value(self):
		self.assertEqual(planned_value(1000, 50), 500)

	def test_schedule_percent_planned_midpoint(self):
		pct = schedule_percent_planned("2026-01-01", "2026-01-11", "2026-01-06")
		self.assertAlmostEqual(pct, 50.0, places=1)

	def test_schedule_percent_before_start(self):
		self.assertEqual(schedule_percent_planned("2026-06-01", "2026-12-01", "2026-01-01"), 0.0)

	@patch("omnexa_construction.evm_metrics.frappe.db.get_all", return_value=[{"planned_cost": 1000, "completion_percent": 40}])
	def test_earned_value_from_boq(self, _ga):
		self.assertEqual(earned_value_from_boq("CNT-1"), 400.0)
