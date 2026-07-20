# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.schedule_critical_path import compute_critical_path


class TestScheduleCriticalPath(FrappeTestCase):
	def test_critical_path_chain(self):
		tasks = [
			{"task_name": "A", "start_date": "2026-01-01", "end_date": "2026-01-05", "duration_days": 5},
			{"task_name": "B", "start_date": "2026-01-06", "end_date": "2026-01-10", "duration_days": 5, "predecessor_task": "A"},
			{"task_name": "C", "start_date": "2026-01-01", "end_date": "2026-01-03", "duration_days": 3},
		]
		critical = compute_critical_path(tasks)
		self.assertIn("A", critical)
		self.assertIn("B", critical)

	def test_missing_predecessor_does_not_crash(self):
		tasks = [
			{"task_name": "A", "start_date": "2026-01-01", "end_date": "2026-01-05", "duration_days": 5},
			{
				"task_name": "B",
				"start_date": "2026-01-06",
				"end_date": "2026-01-10",
				"duration_days": 5,
				"predecessor_task": "SS2 Pile Cap",
			},
		]
		critical = compute_critical_path(tasks)
		self.assertIn("B", critical)
		self.assertIsInstance(critical, list)

	def test_comma_separated_predecessors(self):
		tasks = [
			{"task_name": "A", "start_date": "2026-01-01", "end_date": "2026-01-05", "duration_days": 5},
			{"task_name": "B", "start_date": "2026-01-01", "end_date": "2026-01-03", "duration_days": 3},
			{
				"task_name": "C",
				"start_date": "2026-01-06",
				"end_date": "2026-01-10",
				"duration_days": 5,
				"predecessor_task": "A, B, Missing Task",
			},
		]
		critical = compute_critical_path(tasks)
		self.assertIn("C", critical)
