# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.construction_qs_measurement_sheet.construction_qs_measurement_sheet import (
	import_takeoff_csv,
)


class TestTakeoffCsvImport(FrappeTestCase):
	@patch(
		"omnexa_construction.omnexa_construction.doctype.construction_qs_measurement_sheet.construction_qs_measurement_sheet.frappe.db.get_all",
		return_value=[
			{
				"name": "BOQ-001",
				"cost_code": "03.10",
				"item_description": "Concrete Works",
				"unit_of_measure": "m3",
				"quantity": 100
	}
		],
	)
	def test_import_maps_to_existing_boq_item(self, _boq):
		rows = import_takeoff_csv(
			"CTR-001",
			"cost_code,measured_qty,description,uom\n03.10,125,Concrete,m3\n",
		)
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["boq_item"], "BOQ-001")
		self.assertEqual(rows[0]["previous_qty"], 100)
		self.assertEqual(rows[0]["measured_qty"], 125)

	@patch(
		"omnexa_construction.omnexa_construction.doctype.construction_qs_measurement_sheet.construction_qs_measurement_sheet.frappe.db.get_all",
		return_value=[],
	)
	def test_import_keeps_rows_without_boq_match(self, _boq):
		rows = import_takeoff_csv(
			"CTR-002",
			"code,qty,description,uom\nX.10,15,Unknown Item,m2\n",
		)
		self.assertEqual(len(rows), 1)
		self.assertFalse(rows[0]["boq_item"])
		self.assertEqual(rows[0]["cost_code"], "X.10")
		self.assertEqual(rows[0]["measured_qty"], 15)
