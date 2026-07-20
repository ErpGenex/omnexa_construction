# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.change_order_boq import apply_change_order_to_boq, compute_boq_line_amounts


class TestChangeOrderBoqUpdate(FrappeTestCase):
	def test_compute_boq_line_amounts(self):
		doc = frappe._dict(boq_lines=[frappe._dict(quantity=10, rate=50, amount=0)])
		compute_boq_line_amounts(doc)
		self.assertEqual(doc.boq_lines[0].amount, 500)

	@patch("omnexa_construction.change_order_boq.frappe.db.set_value")
	@patch("omnexa_construction.change_order_boq.frappe.msgprint")
	@patch("omnexa_construction.change_order_boq.frappe.get_doc")
	def test_apply_increments_boq_quantity(self, mock_get_doc, _msg, _set):
		boq = MagicMock()
		boq.project_contract = "CTR-001"
		boq.planned_quantity = 100
		boq.planned_rate = 10
		boq.meta.has_field.return_value = True
		boq.planned_cost = 1000
		mock_get_doc.return_value = boq

		doc = frappe._dict(
			status="Implemented",
			docstatus=1,
			project_contract="CTR-001",
			doctype="Construction Change Order",
			name="CO-001",
			boq_lines=[frappe._dict(boq_item="BOQ-001", quantity=5, rate=12)],
		)
		doc.meta = MagicMock()
		doc.meta.has_field.side_effect = lambda f: f == "boq_applied"
		doc.get = lambda k, d=None: doc[k] if k in doc else d

		apply_change_order_to_boq(doc)
		self.assertEqual(boq.planned_quantity, 105)
		_set.assert_called_once()
