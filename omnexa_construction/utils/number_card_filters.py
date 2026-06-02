from __future__ import annotations

"""Number Card filter helpers — Frappe desk route expects 4-tuples [doctype, field, op, value]."""


def normalize_number_card_filters(document_type: str, filters: list | None) -> list:
	"""Convert 3-tuple filters to 4-tuple for Number Card storage and list navigation."""
	if not filters:
		return []
	out: list = []
	for row in filters:
		if not row:
			continue
		if isinstance(row, (list, tuple)):
			if len(row) == 3:
				field, operator, value = row
				out.append([document_type, field, operator, value])
			elif len(row) == 4:
				out.append(list(row))
			continue
		if isinstance(row, dict):
			for field, value in row.items():
				if isinstance(value, (list, tuple)) and len(value) == 2:
					out.append([document_type, field, value[0], value[1]])
				else:
					out.append([document_type, field, "=", value])
	return out


def fix_number_cards_for_doctype(document_type: str) -> int:
	import json

	import frappe

	fixed = 0
	for row in frappe.get_all(
		"Number Card",
		filters={"document_type": document_type, "type": "Document Type"},
		fields=["name", "filters_json"],
	):
		raw = row.filters_json or "[]"
		try:
			parsed = frappe.parse_json(raw) if isinstance(raw, str) else raw
		except Exception:
			continue
		if not parsed:
			continue
		normalized = normalize_number_card_filters(document_type, parsed)
		if normalized == parsed:
			continue
		frappe.db.set_value(
			"Number Card",
			row.name,
			"filters_json",
			json.dumps(normalized, separators=(",", ":")),
			update_modified=False,
		)
		fixed += 1
	return fixed
