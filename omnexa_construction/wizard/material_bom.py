from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.wizard.catalog_import import (
	ensure_catalog_item,
	ensure_construction_uoms,
	import_material_catalog,
	resolve_item_code,
)
from omnexa_construction.wizard.material_catalog import TRADE_DEFAULT_ITEMS, item_code
from omnexa_construction.wizard.pricing import money
from omnexa_construction.wizard.scaling import LUMP_SUM_UOMS


def _normalize_lump_uom(uom: str | None) -> str:
	return (uom or "").strip().lower().replace(".", "")


def material_row_uom(item: str, boq_uom: str | None) -> str:
	"""BOQ lump-sum UOM (ls) is not valid on material lines — use Item stock UOM."""
	ensure_construction_uoms()
	stock_uom = frappe.db.get_value("Item", item, "stock_uom") or "Nos"
	boq_key = _normalize_lump_uom(boq_uom)
	if boq_key in LUMP_SUM_UOMS or boq_key == "ls":
		uom = stock_uom
	else:
		uom = (boq_uom or "").strip() or stock_uom
	if not frappe.db.exists("UOM", uom):
		uom = stock_uom if frappe.db.exists("UOM", stock_uom) else "Nos"
	return uom


def _resolve_bom_item(trade_code: str | None, *, spec_hint: str, company: str, suffix: str | None = None) -> str | None:
	if suffix:
		code = ensure_catalog_item(suffix, company) or item_code(suffix)
		if frappe.db.exists("Item", code):
			return code
	return resolve_item_code(trade_code, spec_hint=spec_hint, company=company)


def build_material_bom_rows(setup, cost_code: str, trade_code: str | None = None) -> list[dict]:
	"""Material BOM lines for one BOQ cost code from setup details + trade defaults."""
	rows: list[dict] = []
	company = setup.company
	import_material_catalog(company, limit=80)
	ensure_construction_uoms()
	for d in setup.boq_details or []:
		if (d.boq_cost_code or "").strip() != cost_code:
			continue
		mat_amt = flt(d.quantity) * flt(d.material_rate)
		if mat_amt <= 0 and "material" not in (d.spec_description or "").lower():
			continue
		item = resolve_item_code(trade_code, spec_hint=d.spec_description or "", uom=d.unit_of_measure, company=company)
		if not item or not frappe.db.exists("Item", item):
			continue
		qty = max(flt(d.quantity), 0.01)
		rate = money(mat_amt / qty) if mat_amt else 0
		rows.append(
			{
				"item_code": item,
				"quantity": qty,
				"uom": material_row_uom(item, d.unit_of_measure),
				"rate": rate,
				"amount": money(qty * rate) if rate else mat_amt,
				"spec_description": d.spec_description
	}
		)
	if rows:
		return rows

	boq_row = next((r for r in setup.boq_lines if r.cost_code == cost_code and r.include), None)
	if not boq_row or boq_row.is_group:
		return []
	mat_cost = flt(boq_row.material_cost)
	if mat_cost <= 0:
		return []
	trade = trade_code or boq_row.trade_package_code
	suffixes = TRADE_DEFAULT_ITEMS.get(trade or "", ["MAT-RMX-C30"])
	split = mat_cost / max(len(suffixes), 1)
	qty = max(flt(boq_row.quantity), 1)
	for suffix in suffixes:
		code = _resolve_bom_item(trade, spec_hint=boq_row.item_description or "", company=company, suffix=suffix)
		if not code or not frappe.db.exists("Item", code):
			continue
		rate = money(split / qty)
		rows.append(
			{
				"item_code": code,
				"quantity": qty,
				"uom": material_row_uom(code, boq_row.unit_of_measure),
				"rate": rate,
				"amount": money(qty * rate),
				"spec_description": boq_row.item_description
	}
		)
	return rows


def apply_material_bom_to_boq_items(setup, code_to_boq: dict[str, str]) -> int:
	"""Write material_bom child table on each leaf BOQ Item."""
	if not frappe.get_meta("BOQ Item").has_field("material_bom"):
		return 0
	import_material_catalog(setup.company)
	count = 0
	for row in setup.boq_lines or []:
		if not row.include or row.is_group:
			continue
		boq_name = code_to_boq.get(row.cost_code)
		if not boq_name:
			continue
		bom_rows = build_material_bom_rows(setup, row.cost_code, row.trade_package_code)
		if not bom_rows:
			continue
		boq = frappe.get_doc("BOQ Item", boq_name)
		boq.set("material_bom", [])
		for br in bom_rows:
			boq.append("material_bom", br)
		boq.flags.ignore_permissions = True
		boq.save()
		count += 1
	return count
