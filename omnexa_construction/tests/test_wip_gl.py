# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wip_gl import create_wip_snapshot_from_project


class TestWipGl(FrappeTestCase):
	@patch("omnexa_construction.wip_gl._gl_totals_if_available", return_value=(0.0, 0.0))
	@patch("omnexa_construction.wip_gl.certified_ipc_net_total", return_value=8000.0)
	@patch("omnexa_construction.wip_gl.actual_cost_from_boq", return_value=12000.0)
	@patch("omnexa_construction.wip_gl.frappe.db.exists")
	@patch("omnexa_construction.wip_gl.frappe.get_doc")
	@patch("omnexa_construction.wip_gl.frappe.db.get_value")
	def test_create_wip_snapshot_from_project_new(
		self, get_value, get_doc, exists, _ac, _ipc, _gl
	):
		def _exists(name, *args, **kwargs):
			if name == "Project Contract":
				return True
			return False

		exists.side_effect = _exists
		get_value.return_value = frappe._dict(
			company="Test Co", branch="Main", contract_title="Tower A"
		)
		doc = get_doc.return_value
		doc.name = "WIP-0001"
		doc.wip_balance = -4000.0
		create_wip_snapshot_from_project("PC-001", snapshot_date="2026-05-30")
		payload = get_doc.call_args[0][0]
		self.assertEqual(payload["doctype"], "Project WIP Snapshot")
		self.assertEqual(payload["cost_to_date"], 12000.0)
		self.assertEqual(payload["revenue_recognized"], 8000.0)
		doc.insert.assert_called_once()
