from __future__ import annotations

import frappe
from frappe.utils import flt


def site_material_cost_total(boq_item: str | None) -> float:
	if not boq_item:
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(material_consumed_cost), 0)
		FROM `tabSite Daily Report`
		WHERE boq_item = %s AND docstatus < 2
		""",
		(boq_item,),
	)
	return flt(row[0][0] if row else 0)


def timesheet_labor_cost_total(boq_item: str | None) -> float:
	if not boq_item or not frappe.db.exists("DocType", "Timesheet Entry"):
		return 0.0
	meta = frappe.get_meta("Timesheet Entry")
	if not meta.has_field("boq_item"):
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(
			COALESCE(cost_amount, hours * COALESCE(cost_rate, billing_rate, 0))
		), 0)
		FROM `tabTimesheet Entry`
		WHERE boq_item = %s AND docstatus < 2
		""",
		(boq_item,),
	)
	return flt(row[0][0] if row else 0)


def equipment_usage_cost_total(boq_item: str | None) -> float:
	if not boq_item or not frappe.db.exists("DocType", "Construction Equipment Usage"):
		return 0.0
	row = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(total_cost), 0)
		FROM `tabConstruction Equipment Usage`
		WHERE boq_item = %s AND docstatus < 2
		""",
		(boq_item,),
	)
	return flt(row[0][0] if row else 0)


def boq_actual_cost_breakdown(boq_item: str | None) -> dict:
	material = site_material_cost_total(boq_item)
	labor = timesheet_labor_cost_total(boq_item)
	equipment = equipment_usage_cost_total(boq_item)
	return {
		"material": material,
		"labor": labor,
		"equipment": equipment,
		"total": material + labor + equipment,
	}


def recompute_boq_actual_cost(boq_item: str | None) -> float:
	if not boq_item or not frappe.db.exists("BOQ Item", boq_item):
		return 0.0
	breakdown = boq_actual_cost_breakdown(boq_item)
	frappe.db.set_value(
		"BOQ Item",
		boq_item,
		"actual_cost",
		breakdown["total"],
		update_modified=False,
	)
	return breakdown["total"]


def refresh_linked_boq_actual_cost(doc, method=None) -> None:
	"""Hook for Site Daily Report, Timesheet Entry, Equipment Usage."""
	if getattr(frappe.flags, "in_import", False):
		return
	boq_item = getattr(doc, "boq_item", None)
	if boq_item:
		recompute_boq_actual_cost(boq_item)
	old = doc.get_doc_before_save() if not doc.is_new() else None
	old_boq = getattr(old, "boq_item", None) if old else None
	if old_boq and old_boq != boq_item:
		recompute_boq_actual_cost(old_boq)
