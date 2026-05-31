from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.wizard.catalog_import import import_material_catalog, resolve_item_code
from omnexa_construction.wizard.material_catalog import TRADE_DEFAULT_ITEMS, item_code
from omnexa_construction.wizard.pricing import money


def build_material_bom_rows(setup, cost_code: str, trade_code: str | None = None) -> list[dict]:
	"""Material BOM lines for one BOQ cost code from setup details + trade defaults."""
	rows: list[dict] = []
	company = setup.company
	for d in setup.boq_details or []:
		if (d.boq_cost_code or "").strip() != cost_code:
			continue
		mat_amt = flt(d.quantity) * flt(d.material_rate)
		if mat_amt <= 0 and "material" not in (d.spec_description or "").lower():
			continue
		item = resolve_item_code(trade_code, spec_hint=d.spec_description or "", uom=d.unit_of_measure, company=company)
		if not item:
			continue
		qty = max(flt(d.quantity), 0.01)
		rate = money(mat_amt / qty) if mat_amt else 0
		rows.append(
			{
				"item_code": item,
				"quantity": qty,
				"uom": d.unit_of_measure or frappe.db.get_value("Item", item, "stock_uom"),
				"rate": rate,
				"amount": money(qty * rate) if rate else mat_amt,
				"spec_description": d.spec_description,
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
		code = item_code(suffix)
		if not frappe.db.exists("Item", code):
			code = resolve_item_code(trade, company=company)
		if not code:
			continue
		rate = money(split / qty)
		rows.append(
			{
				"item_code": code,
				"quantity": qty,
				"uom": boq_row.unit_of_measure or frappe.db.get_value("Item", code, "stock_uom"),
				"rate": rate,
				"amount": money(qty * rate),
				"spec_description": boq_row.item_description,
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
