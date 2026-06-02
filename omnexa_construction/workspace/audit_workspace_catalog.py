"""One-off audit: print workspace catalog gaps. Run via bench execute."""

from __future__ import annotations

import frappe

from omnexa_construction.workspace.construction_workspace import WORKSPACE_SECTIONS, _link_target_exists


def audit_workspace_catalog():
	catalog = set()
	missing_db = []
	for section, items in WORKSPACE_SECTIONS:
		for lt, lto, label, icon, is_r in items:
			catalog.add((lt, lto))
			if not _link_target_exists(lt, lto):
				missing_db.append({"section": section, "type": lt, "link_to": lto, "label": label})

	dts = frappe.get_all(
		"DocType",
		filters={"module": "Omnexa Construction", "istable": 0},
		pluck="name",
	)
	skip = {"Construction Integration Settings"}
	not_in_catalog = [d for d in sorted(dts) if ("DocType", d) not in catalog and d not in skip]

	reports = frappe.get_all("Report", filters={"module": "Omnexa Construction"}, pluck="name")
	reports_not_in = [r for r in sorted(reports) if ("Report", r) not in catalog]

	pages = [
		"construction-project-wizard",
		"construction-executive-dashboard",
		"construction-site-mobile",
		"construction-schedule-gantt",
		"construction-ifc-viewer",
		"construction-bi-executive",
		"construction-hse-dashboard",
	]
	pages_not_in = [p for p in pages if ("Page", p) not in catalog]

	return {
		"missing_from_db": missing_db,
		"doctypes_not_in_catalog": not_in_catalog,
		"reports_not_in_catalog": reports_not_in,
		"pages_not_in_catalog": pages_not_in,
		"catalog_link_count": len(catalog),
	}
