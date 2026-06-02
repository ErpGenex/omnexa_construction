# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate import (
	suggest_completion_percent_from_schedule,
)


class TestIpcScheduleSuggestion(FrappeTestCase):
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.suggest_boq_completion_percent",
		return_value=22.0,
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.get_value",
		return_value=35.0,
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.exists",
		side_effect=lambda dt, name=None: True if dt == "DocType" else False,
	)
	def test_prefers_wbs_progress_when_available(self, _exists, _get_value, _boq):
		out = suggest_completion_percent_from_schedule("CTR-1", pm_wbs_task="WBS-1")
		self.assertEqual(out["source"], "schedule_wbs")
		self.assertEqual(out["suggested_percent"], 35.0)

	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.suggest_boq_completion_percent",
		return_value=18.0,
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.schedule_percent_planned",
		return_value=57.0,
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.get_all",
		return_value=[],
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.get_value",
		return_value={"planned_start": "2026-01-01", "planned_completion": "2026-12-31"},
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.exists",
		side_effect=lambda dt, name=None: True if dt == "DocType" else False,
	)
	def test_fallbacks_to_active_baseline(self, _exists, _get_value, _get_all, _sched, _boq):
		out = suggest_completion_percent_from_schedule("CTR-2")
		self.assertEqual(out["source"], "schedule_baseline")
		self.assertEqual(out["suggested_percent"], 57.0)

	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.suggest_boq_completion_percent",
		return_value=41.0,
	)
	@patch(
		"omnexa_construction.omnexa_construction.doctype.ipc_certificate.ipc_certificate.frappe.db.exists",
		return_value=False,
	)
	def test_fallbacks_to_boq_when_no_schedule_inputs(self, _exists, _boq):
		out = suggest_completion_percent_from_schedule("CTR-3")
		self.assertEqual(out["source"], "boq")
		self.assertEqual(out["suggested_percent"], 41.0)
