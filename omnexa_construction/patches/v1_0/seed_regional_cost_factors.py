# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe


SEEDS = (
	("EG-CAIRO", "Cairo / Giza", 1.0, 1),
	("EG-ALEX", "Alexandria", 0.96, 0),
	("EG-UPPER", "Upper Egypt", 0.88, 0),
	("GCC-RIYADH", "Riyadh / KSA", 1.14, 0),
	("GCC-DUBAI", "Dubai / UAE", 1.22, 0),
	("EU-WEST", "Western Europe", 1.35, 0),
)


def execute():
	if not frappe.db.exists("DocType", "Regional Cost Factor"):
		return
	for company in frappe.get_all("Company", pluck="name"):
		default_set = False
		for code, name, factor, is_default in SEEDS:
			if frappe.db.exists("Regional Cost Factor", {"region_code": code, "company": company}):
				continue
			use_default = is_default and not default_set
			frappe.get_doc(
				{
					"doctype": "Regional Cost Factor",
					"region_code": code,
					"region_name": name,
					"company": company,
					"cost_factor": factor,
					"is_default": use_default,
					"disabled": 0,
				}
			).insert(ignore_permissions=True)
			if use_default:
				default_set = True
