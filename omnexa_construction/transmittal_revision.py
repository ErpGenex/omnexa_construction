# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""CDE revision history and transmittal revision helpers."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def get_cde_revision_chain(document_name: str) -> list[dict]:
	"""Return revision chain for a CDE document number on a contract."""
	doc = frappe.get_doc("Construction CDE Document", document_name)
	if not doc.document_number:
		return []

	rows = frappe.get_all(
		"Construction CDE Document",
		filters={
			"project_contract": doc.project_contract,
			"document_number": doc.document_number,
			"docstatus": ["<", 2]},
		fields=[
			"name",
			"revision",
			"approval_status",
			"issued_date",
			"superseded_by",
			"cde_status",
		],
		order_by="issued_date asc, creation asc",
	)
	return rows


@frappe.whitelist()
def compare_transmittal_revisions(transmittal_a: str, transmittal_b: str) -> dict:
	"""Compare document lines between two transmittals by document_no."""
	a = frappe.get_doc("Construction Document Transmittal", transmittal_a)
	b = frappe.get_doc("Construction Document Transmittal", transmittal_b)
	index_a = {(r.document_no or r.document_title): r for r in (a.items or [])}
	index_b = {(r.document_no or r.document_title): r for r in (b.items or [])}

	added = [k for k in index_b if k not in index_a]
	removed = [k for k in index_a if k not in index_b]
	revised = []
	for key in index_a:
		if key not in index_b:
			continue
		ra, rb = index_a[key], index_b[key]
		if (ra.revision_no or "") != (rb.revision_no or ""):
			revised.append(
				{
					"document": key,
					"from_revision": ra.revision_no,
					"to_revision": rb.revision_no
	}
			)
	return {"added": added, "removed": removed, "revised": revised
	}
