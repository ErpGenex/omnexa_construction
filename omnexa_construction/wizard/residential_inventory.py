from __future__ import annotations

import frappe
from frappe.utils import cint, flt


RESIDENTIAL_BUILDING_TYPES = frozenset(
	{
		"villa",
		"residential_building",
		"social_housing",
	}
)


def sync_residential_inventory_from_setup(setup, project_contract: str) -> dict:
	"""Create plot + unit inventory rows for residential developer projects."""
	if setup.building_type not in RESIDENTIAL_BUILDING_TYPES:
		return {"plots": 0, "units": 0}
	if not frappe.db.exists("DocType", "Construction Plot Unit"):
		return {"plots": 0, "units": 0}

	plots = units = 0
	unit_count = max(cint(setup.unit_count) or 1, 1)
	plot_area = flt(setup.plot_area_m2)
	per_plot = plot_area / unit_count if plot_area else 0
	phases = [p.phase_code for p in (setup.phases or []) if p.phase_code] or ["PH-01"]

	for i in range(1, unit_count + 1):
		plot_no = f"P-{i:03d}"
		if not frappe.db.exists(
			"Construction Plot Unit",
			{"project_contract": project_contract, "plot_number": plot_no},
		):
			frappe.get_doc(
				{
					"doctype": "Construction Plot Unit",
					"project_contract": project_contract,
					"plot_number": plot_no,
					"plot_area_m2": per_plot or flt(setup.plot_area_m2),
					"phase_code": phases[(i - 1) % len(phases)],
					"plot_status": "Available",
					"unit_typology": setup.building_type,
					"company": setup.company,
					"branch": setup.branch,
				}
			).insert(ignore_permissions=True)
			plots += 1

		unit_no = f"U-{i:03d}"
		if frappe.db.exists(
			"DocType", "Construction Residential Unit"
		) and not frappe.db.exists(
			"Construction Residential Unit",
			{"project_contract": project_contract, "unit_number": unit_no},
		):
			gfa = flt(setup.gross_floor_area_m2)
			sellable = gfa / unit_count if gfa else 0
			frappe.get_doc(
				{
					"doctype": "Construction Residential Unit",
					"project_contract": project_contract,
					"unit_number": unit_no,
					"plot_number": plot_no,
					"floor_level": ((i - 1) % max(cint(setup.number_of_floors) or 1, 1)) + 1,
					"phase_code": phases[(i - 1) % len(phases)],
					"sellable_area_m2": sellable,
					"unit_status": "Planned",
					"company": setup.company,
					"branch": setup.branch,
				}
			).insert(ignore_permissions=True)
			units += 1

	return {"plots": plots, "units": units}
