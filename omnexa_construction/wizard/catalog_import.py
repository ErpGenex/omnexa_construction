from __future__ import annotations

import frappe
from frappe import _

from omnexa_construction.wizard.material_catalog import ITEM_PREFIX, full_catalog, item_code


CONSTRUCTION_UOMS: tuple[str, ...] = (
	"ls",
	"Lump Sum",
	"m³",
	"Bag",
	"Ton",
	"Nos",
	"Meter",
	"m²",
	"Liter",
	"Roll",
	"Kg",
	"CuM",
)


def ensure_construction_uoms() -> None:
	for uom_name in CONSTRUCTION_UOMS:
		_ensure_uom(uom_name)


def _item_has_arabic_name_field() -> bool:
	try:
		return bool(frappe.get_meta("Item").has_field("item_name_ar"))
	except Exception:
		return False


def _ensure_uom(uom_name: str) -> None:
	if uom_name and not frappe.db.exists("UOM", uom_name):
		frappe.get_doc({"doctype": "UOM", "uom_name": uom_name
	}).insert(ignore_permissions=True)


def import_material_catalog(company: str, *, limit: int = 200) -> dict:
	"""Idempotent import of construction material Items for a company."""
	if not frappe.db.exists("DocType", "Item"):
		return {"created": 0, "skipped": 0, "total": 0
	}
	ensure_construction_uoms()
	has_ar = _item_has_arabic_name_field()
	created = skipped = 0
	for suffix, name_en, name_ar, uom, product_type, classification in full_catalog()[:limit]:
		_ensure_uom(uom)
		code = item_code(suffix)
		if frappe.db.get_value("Item", {"item_code": code, "company": company
	}, "name"):
			skipped += 1
			continue
		payload: dict = {
			"doctype": "Item",
			"item_code": code,
			"item_name": name_en,
			"company": company,
			"stock_uom": uom,
			"product_type": product_type,
			"is_stock_item": 1,
			"is_purchase_item": 1,
			"is_sales_item": 0,
			"classification_code": classification
	}
		if has_ar:
			payload["item_name_ar"] = name_ar
		frappe.get_doc(payload).insert(ignore_permissions=True)
		created += 1
	return {"created": created, "skipped": skipped, "total": len(full_catalog()[:limit])
	}


def resolve_item_code(
	trade_code: str | None = None,
	*,
	spec_hint: str = "",
	uom: str = "",
	company: str | None = None,
) -> str | None:
	"""Pick best catalog item for a BOQ line or detail."""
	from omnexa_construction.wizard.material_catalog import TRADE_DEFAULT_ITEMS

	if company:
		import_material_catalog(company, limit=50)

	hint = (spec_hint or "").lower()
	rules = [
		("steel", "MAT-STEEL-R16"),
		("rebar", "MAT-STEEL-R16"),
		("concrete", "MAT-RMX-C30"),
		("cement", "MAT-CEM-OPC"),
		("sand", "MAT-SAND-FINE"),
		("asphalt", "MAT-ASPHALT"),
		("tile", "MAT-TILE-60"),
		("paint", "MAT-PAINT-INT"),
		("plumb", "MAT-PVC-110"),
		("pipe", "MAT-PVC-110"),
		("cable", "MAT-CABLE-16"),
		("electr", "MAT-CABLE-16"),
		("hvac", "MAT-DUCT"),
		("gypsum", "MAT-GYPSUM"),
		("glass", "MAT-GLASS-10"),
	]
	for keyword, suffix in rules:
		if keyword in hint:
			code = item_code(suffix)
			if _item_exists(code, company):
				return code
	if trade_code:
		for suffix in TRADE_DEFAULT_ITEMS.get(trade_code, ["MAT-RMX-C30"]):
			code = item_code(suffix)
			if _item_exists(code, company):
				return code
	for suffix in ("MAT-RMX-C30", "MAT-SAND-FINE"):
		code = item_code(suffix)
		if _item_exists(code, company):
			return code
	return None


def _item_exists(code: str, company: str | None) -> bool:
	if company and frappe.db.get_value("Item", {"item_code": code, "company": company
	}, "name"):
		return True
	return bool(frappe.db.get_value("Item", {"item_code": code
	}, "name"))


def ensure_catalog_item(suffix: str, company: str) -> str | None:
	"""Create one catalog Item for company if missing (wizard BOM / PR)."""
	ensure_construction_uoms()
	code = item_code(suffix)
	if _item_exists(code, company):
		return code
	for row in full_catalog():
		if row[0] != suffix:
			continue
		_, name_en, name_ar, uom, product_type, classification = row
		_ensure_uom(uom)
		has_ar = _item_has_arabic_name_field()
		payload: dict = {
			"doctype": "Item",
			"item_code": code,
			"item_name": name_en,
			"company": company,
			"stock_uom": uom,
			"product_type": product_type,
			"is_stock_item": 1,
			"is_purchase_item": 1,
			"is_sales_item": 0,
			"classification_code": classification
	}
		if has_ar:
			payload["item_name_ar"] = name_ar
		frappe.get_doc(payload).insert(ignore_permissions=True)
		return code
	return None
