# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.schedule_gantt import get_schedule_gantt_data


class TestScheduleGantt(FrappeTestCase):
	@patch("omnexa_construction.schedule_critical_path.compute_critical_path", return_value=[])
	@patch("omnexa_construction.schedule_gantt.frappe.get_all")
	@patch("omnexa_construction.schedule_gantt._resolve_schedule_baseline")
	def test_gantt_returns_task_payload(self, mock_resolve, mock_get_all, _mock_cpm):
		mock_resolve.return_value = {
			"name": "BL-1",
			"planned_start": "2026-01-01",
			"planned_completion": "2026-12-31",
			"baseline_name": "BL1",
			"docstatus": 1,
		}
		mock_get_all.return_value = [
			{
				"task_name": "Concrete",
				"start_date": "2026-02-01",
				"end_date": "2026-03-01",
				"duration_days": 28,
				"boq_item": "BOQ-1",
				"cost_code": "03.10",
				"progress_percent": 40,
				"is_milestone": 0,
			}
		]

		with patch("omnexa_construction.schedule_gantt.frappe.db.get_value", return_value=55):
			out = get_schedule_gantt_data("CTR-1")
		self.assertEqual(len(out["tasks"]), 1)
		self.assertEqual(out["tasks"][0]["progress"], 55)
		self.assertFalse(out["baseline_is_draft"])

	@patch("omnexa_construction.schedule_critical_path.compute_critical_path", return_value=[])
	@patch("omnexa_construction.schedule_gantt.frappe.get_all")
	@patch("omnexa_construction.schedule_gantt._resolve_schedule_baseline")
	def test_gantt_includes_draft_baseline(self, mock_resolve, mock_get_all, _mock_cpm):
		mock_resolve.return_value = {
			"name": "BL-DRAFT",
			"planned_start": "2026-01-01",
			"planned_completion": "2026-12-31",
			"baseline_name": "Draft",
			"docstatus": 0,
		}
		mock_get_all.return_value = [
			{
				"task_name": "Excavation",
				"start_date": "2026-02-01",
				"end_date": "2026-03-01",
				"duration_days": 28,
				"boq_item": None,
				"cost_code": "03.10",
				"progress_percent": 10,
				"is_milestone": 0,
			}
		]

		out = get_schedule_gantt_data("CTR-DRAFT")
		self.assertTrue(out["baseline_is_draft"])
		self.assertEqual(len(out["tasks"]), 1)
