# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""NCR closure SLA tracking (ISO 45001)."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate

SLA_DAYS = {"Minor": 14, "Major": 7, "Critical": 3
	}


def apply_ncr_sla(doc, method=None) -> None:
	if doc.doctype != "Construction NCR":
		return
	meta = frappe.get_meta("Construction NCR")
	if not meta.has_field("target_close_date"):
		return
	days = SLA_DAYS.get(doc.severity or "Minor", 14)
	if doc.ncr_date and not doc.target_close_date:
		doc.target_close_date = add_days(getdate(doc.ncr_date), days)
	if meta.has_field("is_sla_breached") and doc.status != "Closed":
		due = doc.target_close_date
		doc.is_sla_breached = 1 if due and getdate() > getdate(due) else 0


def mark_ncr_sla_breaches_daily():
	if not frappe.db.exists("DocType", "Construction NCR"):
		return
	meta = frappe.get_meta("Construction NCR")
	if not meta.has_field("is_sla_breached"):
		return
	for name in frappe.get_all(
		"Construction NCR",
		filters={"status": ["!=", "Closed"], "docstatus": ["<", 2]},
		pluck="name",
	):
		doc = frappe.get_doc("Construction NCR", name)
		apply_ncr_sla(doc)
		if doc.is_sla_breached:
			doc.db_set("is_sla_breached", 1, update_modified=True)
