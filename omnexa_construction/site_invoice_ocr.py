# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Site invoice OCR + BOQ line match (Phase 14.4 — MVP with manual fallback)."""

from __future__ import annotations

import re

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def parse_site_invoice_text(raw_text: str, project_contract: str) -> dict:
	"""Parse pasted invoice text; optional OCR upstream supplies raw_text."""
	lines = []
	for row in (raw_text or "").splitlines():
		row = row.strip()
		if not row:
			continue
		amounts = re.findall(r"[\d,]+\.?\d*", row.replace(",", ""))
		qty = flt(amounts[0]) if amounts else 0
		rate = flt(amounts[1]) if len(amounts) > 1 else 0
		amount = flt(amounts[2]) if len(amounts) > 2 else qty * rate
		desc = re.sub(r"[\d,\.]+", "", row).strip(" -\t")
		lines.append({"description": desc, "qty": qty, "rate": rate, "amount": amount
	})

	matches = match_lines_to_boq(project_contract, lines)
	return {
		"parsed_lines": lines,
		"boq_matches": matches,
		"ocr_mode": "text_fallback",
		"message": _("Parsed {0} line(s). Review BOQ matches before posting.").format(len(lines))
	}


def match_lines_to_boq(project_contract: str, lines: list[dict]) -> list[dict]:
	meta = frappe.get_meta("BOQ Item")
	desc_field = "item_description" if meta.has_field("item_description") else "description"
	fields = ["name"]
	if meta.has_field(desc_field):
		fields.append(desc_field)
	if meta.has_field("item_code"):
		fields.append("item_code")
	if meta.has_field("quantity"):
		fields.append("quantity")
	elif meta.has_field("qty"):
		fields.append("qty")
	if meta.has_field("unit_cost"):
		fields.append("unit_cost")
	elif meta.has_field("rate"):
		fields.append("rate")
	boq = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "docstatus": ["<", 2]},
		fields=fields,
		limit=500,
	)
	out = []
	for line in lines:
		desc = (line.get("description") or "").lower()
		best = None
		best_score = 0
		for item in boq:
			item_desc = (getattr(item, desc_field, None) or "").lower()
			score = _similarity(desc, item_desc)
			if score > best_score:
				best_score = score
				best = item
		out.append(
			{
				"line": line,
				"boq_item": best.name if best and best_score >= 0.35 else None,
				"match_score": round(best_score, 2)}
		)
	return out


def _similarity(a: str, b: str) -> float:
	if not a or not b:
		return 0.0
	if a in b or b in a:
		return 0.9
	aw = set(a.split())
	bw = set(b.split())
	if not aw or not bw:
		return 0.0
	return len(aw & bw) / len(aw | bw)
