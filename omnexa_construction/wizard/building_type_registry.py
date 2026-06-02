# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Single source of truth for wizard building / project types (Select options + API)."""

from __future__ import annotations

from omnexa_construction.wizard.template_packs import BUILDING_TYPE_META


def building_type_select_options() -> str:
	"""Newline-separated options for DocType Select fields."""
	return "\n".join(sorted(BUILDING_TYPE_META.keys()))


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
				"has_template": bool(meta.get("template_code")),
			}
		)
	return out
