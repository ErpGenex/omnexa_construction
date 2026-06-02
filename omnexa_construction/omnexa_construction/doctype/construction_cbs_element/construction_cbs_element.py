# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionCBSElement(Document):
	def validate(self):
		if self.parent_cbs_element == self.name:
			frappe.throw(_("CBS element cannot be its own parent."), title=_("CBS"))


def suggest_cbs_for_cost_code(cost_code: str | None) -> str | None:
	"""Return CBS element name matching BOQ cost_code prefix (longest match)."""
	code = (cost_code or "").strip()
	if not code:
		return None
	prefix = code.split(".")[0] if "." in code else code[:2]
	if not prefix:
		return None
	rows = frappe.get_all(
		"Construction CBS Element",
		filters={"cost_code_prefix": prefix},
		fields=["name", "cost_code_prefix"],
		limit_page_length=20,
	)
	if not rows:
		return None
	rows.sort(key=lambda r: len(r.get("cost_code_prefix") or ""), reverse=True)
	return rows[0].get("name")
