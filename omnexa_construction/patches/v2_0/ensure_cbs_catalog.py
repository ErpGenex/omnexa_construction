# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Seed standard construction CBS elements mapped to BOQ cost-code prefixes."""

from __future__ import annotations

SEED_ROWS = [
	("CBS-00", "00", "Preliminaries & General"),
	("CBS-01", "01", "Site & Earthworks"),
	("CBS-02", "02", "Substructure / Foundations"),
	("CBS-03", "03", "Superstructure / Concrete"),
	("CBS-04", "04", "Masonry & Blockwork"),
	("CBS-05", "05", "Roofing & Waterproofing"),
	("CBS-06", "06", "Facades & Cladding"),
	("CBS-07", "07", "Architectural Finishes"),
	("CBS-08", "08", "Joinery & Fit-out"),
	("CBS-09", "09", "Mechanical (HVAC)"),
	("CBS-10", "10", "Plumbing & Drainage"),
	("CBS-11", "11", "Electrical & ELV"),
	("CBS-12", "12", "Lifts & Vertical Transport"),
	("CBS-13", "13", "External Works & Landscaping"),
	("CBS-14", "14", "Testing & Commissioning"),
	("CBS-15", "15", "Provisional Sums"),
	("CBS-16", "16", "Contingency & Risk"),
]


def execute():
	import frappe

	for cbs_code, prefix, title in SEED_ROWS:
		if frappe.db.exists("Construction CBS Element", cbs_code):
			frappe.db.set_value(
				"Construction CBS Element",
				cbs_code,
				{"title": title, "cost_code_prefix": prefix},
				update_modified=False,
			)
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Construction CBS Element",
				"cbs_code": cbs_code,
				"title": title,
				"cost_code_prefix": prefix,
				"is_group": 0,
			}
		)
		doc.insert(ignore_permissions=True)
	frappe.db.commit()
