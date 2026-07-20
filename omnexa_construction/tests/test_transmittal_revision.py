# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.transmittal_revision import compare_transmittal_revisions


class TestTransmittalRevision(FrappeTestCase):
	def test_compare_detects_revision_change(self):
		a = type(
			"T",
			(),
			{"items": [type("L", (), {"document_no": "DRW-001", "document_title": "Drawing", "revision_no": "A"})()]
	},
		)()
		b = type(
			"T",
			(),
			{"items": [type("L", (), {"document_no": "DRW-001", "document_title": "Drawing", "revision_no": "B"})()]
	},
		)()
		import omnexa_construction.transmittal_revision as mod

		orig = mod.frappe.get_doc
		mod.frappe.get_doc = lambda dt, name: a if name == "A" else b
		try:
			out = compare_transmittal_revisions("A", "B")
		finally:
			mod.frappe.get_doc = orig
		self.assertEqual(len(out["revised"]), 1)
		self.assertEqual(out["revised"][0]["to_revision"], "B")
