from __future__ import annotations

import frappe
from frappe.utils import today

from omnexa_construction.fidic_compliance import mark_time_barred_notices, refresh_fidic_notice_compliance


def mark_overdue_fidic_notices():
	"""Daily job: mark open FIDIC notices past response due date as Overdue."""
	if not frappe.db.exists("DocType", "Construction FIDIC Notice"):
		return
	for name in frappe.get_all(
		"Construction FIDIC Notice",
		filters={"status": "Open", "response_due_date": ["<", today()]},
		pluck="name",
	):
		frappe.db.set_value("Construction FIDIC Notice", name, "status", "Overdue", update_modified=True)
	mark_time_barred_notices()
