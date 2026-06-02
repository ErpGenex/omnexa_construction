# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.schedule_gantt import get_schedule_gantt_data


class TestScheduleGantt(FrappeTestCase):
	@patch("omnexa_construction.schedule_gantt.frappe.db.get_value")
	@patch("omnexa_construction.schedule_gantt.frappe.get_all")
	def test_gantt_returns_task_payload(self, mock_get_all, mock_get_value):
		mock_get_value.return_value = {
			"name": "BL-1",
			"planned_start": "2026-01-01",
			"planned_completion": "2026-12-31",
			"baseline_name": "BL1",
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

		def _boq_value(doctype, name, fieldname=None, **kwargs):
			if doctype == "BOQ Item" and fieldname == "completion_percent":
				return 55
			return mock_get_value.return_value

		with patch("omnexa_construction.schedule_gantt.frappe.db.get_value", side_effect=_boq_value):
			out = get_schedule_gantt_data("CTR-1")
		self.assertEqual(len(out["tasks"]), 1)
		self.assertEqual(out["tasks"][0]["progress"], 55)
