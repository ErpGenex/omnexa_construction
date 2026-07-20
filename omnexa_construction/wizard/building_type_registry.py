# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Single source of truth for wizard building / project types (Select options + API)."""

from __future__ import annotations

from omnexa_construction.wizard.template_packs import BUILDING_TYPE_META


def building_type_select_options() -> str:
	"""Newline-separated options for DocType Select fields (leading blank = optional empty)."""
	return "\n" + "\n".join(sorted(BUILDING_TYPE_META.keys()))


BUILDING_TYPE_FIELD_DOCTYPES = (
	"Construction Project Setup",
	"Construction BOQ Template",
	"Project Contract",
	"Regional Cost Factor",
)


def sync_building_type_select_options() -> dict:
	"""Push catalog building types to Select field options (DocType + Property Setter)."""
	import frappe

	options = building_type_select_options()
	updated = []
	for dt in BUILDING_TYPE_FIELD_DOCTYPES:
		if not frappe.db.exists("DocType", dt):
			continue
		if not frappe.get_meta(dt).has_field("building_type"):
			continue
		ps_name = f"{dt}-building_type-options"
		if frappe.db.exists("Property Setter", ps_name):
			frappe.db.set_value("Property Setter", ps_name, "value", options, update_modified=False)
		else:
			frappe.make_property_setter(
				{
					"doctype": dt,
					"doctype_or_field": "DocField",
					"fieldname": "building_type",
					"property": "options",
					"property_type": "Text",
					"value": options
	},
				ignore_validate=True,
			)
		updated.append(dt)
		frappe.clear_cache(doctype=dt)
	return {"options_count": len(BUILDING_TYPE_META), "doctypes": updated
	}


def segment_for_building_type(code: str | None) -> str:
	meta = BUILDING_TYPE_META.get((code or "").strip(), {})
	return meta.get("segment") or "Other"


def list_building_types_for_api() -> list[dict]:
	out = []
	for code, meta in sorted(BUILDING_TYPE_META.items(), key=lambda x: x[1].get("label_en", x[0])):
		out.append(
			{
				"code": code,
				"label_en": meta.get("label_en", code),
				"label_ar": meta.get("label_ar", code),
				"segment": meta.get("segment", "Other"),
				"template_code": meta.get("template_code"),
				"has_template": bool(meta.get("template_code"))
	}
		)
	return out
