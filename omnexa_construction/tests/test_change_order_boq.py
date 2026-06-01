# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.change_order_boq import compute_boq_line_amounts


class TestChangeOrderBoq(FrappeTestCase):
	def test_compute_boq_line_amounts(self):
		doc = frappe._dict(
			boq_lines=[
				frappe._dict(quantity=10, rate=100, amount=0),
				frappe._dict(quantity=2, rate=50, amount=0),
			]
		)
		compute_boq_line_amounts(doc)
		self.assertEqual(doc.boq_lines[0].amount, 1000)
		self.assertEqual(doc.boq_lines[1].amount, 100)
