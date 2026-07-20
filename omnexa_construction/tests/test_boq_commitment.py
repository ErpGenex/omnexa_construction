# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.boq_commitment import committed_amount_for_boq


class TestBoqCommitment(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		if not frappe.get_meta("BOQ Item").has_field("committed_cost"):
			from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

			create_custom_fields(
				{
					"BOQ Item": [
						{
							"fieldname": "committed_cost",
							"label": "Committed Cost (PO)",
							"fieldtype": "Currency",
							"read_only": 1,
							"insert_after": "actual_cost",
							"module": "Omnexa Construction",
						}
					]
				},
				update=True,
			)
			frappe.clear_cache()

	def test_committed_amount_no_crash(self):
		self.assertEqual(committed_amount_for_boq("NONEXISTENT-BOQ"), 0.0)

	def test_boq_has_committed_field(self):
		meta = frappe.get_meta("BOQ Item")
		self.assertTrue(meta.has_field("committed_cost"))
