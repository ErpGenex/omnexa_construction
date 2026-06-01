# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""FIDIC notice time-bar and linkage helpers."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate


# Default notice periods (days) by governing standard keyword
TIME_BAR_DAYS = {
	"FIDIC Red Book 2017": 28,
	"FIDIC Yellow Book 2017": 28,
	"FIDIC Silver Book 2017": 28,
	"FIDIC": 28,
	"NEC4 ECC": 42,
	"NEC4": 42,
}


def time_bar_days_for_contract(project_contract: str) -> int:
	standard = frappe.db.get_value("Project Contract", project_contract, "governing_standard") or ""
	for key, days in TIME_BAR_DAYS.items():
		if key.lower() in (standard or "").lower():
			return days
	return 28


def compute_notice_due_date(notice_date, project_contract: str):
	if not notice_date:
		return None
	days = time_bar_days_for_contract(project_contract)
	return add_days(getdate(notice_date), days)


def refresh_fidic_notice_compliance(doc) -> None:
	"""Set notice_due_date and is_time_barred on Construction FIDIC Notice."""
	if not doc.get("notice_date") or not doc.get("project_contract"):
		return
	if doc.meta.has_field("notice_due_date") and not doc.notice_due_date:
		doc.notice_due_date = compute_notice_due_date(doc.notice_date, doc.project_contract)
	if doc.meta.has_field("is_time_barred"):
		due = doc.get("notice_due_date") or compute_notice_due_date(doc.notice_date, doc.project_contract)
		if due and getdate() > getdate(due) and doc.status in ("Open", "Overdue"):
			doc.is_time_barred = 1
		elif doc.status in ("Acknowledged", "Closed"):
			doc.is_time_barred = 0


def validate_fidic_notice_doc(doc, method=None):
	refresh_fidic_notice_compliance(doc)


def mark_time_barred_notices():
	"""Daily: flag open notices past due date."""
	if not frappe.db.exists("DocType", "Construction FIDIC Notice"):
		return
	meta = frappe.get_meta("Construction FIDIC Notice")
	if not meta.has_field("is_time_barred"):
		return
	for name in frappe.get_all(
		"Construction FIDIC Notice",
		filters={"status": ["in", ["Open", "Overdue"]], "docstatus": ["<", 2]},
		pluck="name",
	):
		doc = frappe.get_doc("Construction FIDIC Notice", name)
		refresh_fidic_notice_compliance(doc)
		if doc.is_time_barred:
			doc.db_set("is_time_barred", 1, update_modified=True)
