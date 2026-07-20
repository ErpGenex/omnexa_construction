# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Subcontract compliance expiry refresh and alerts."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate, today


def refresh_compliance_status(doc, method=None) -> None:
	lines = doc.get("compliance_documents") or []
	if not lines:
		return
	changed = False
	as_of = getdate(today())
	for row in lines:
		if not row.expiry_date:
			continue
		expiry = getdate(row.expiry_date)
		new_status = "Valid"
		if expiry < as_of:
			new_status = "Expired"
		elif expiry <= add_days(as_of, 30):
			new_status = "Expiring"
		if row.status != new_status:
			row.status = new_status
			changed = True
	if changed and not frappe.flags.in_import:
		doc.db_update()


def mark_expired_compliance_daily() -> None:
	if not frappe.db.exists("DocType", "Subcontract Compliance Line"):
		return
	frappe.db.sql(
		"""
		UPDATE `tabSubcontract Compliance Line`
		SET status = 'Expired'
		WHERE expiry_date IS NOT NULL AND expiry_date < %s AND status != 'Expired'
		""",
		today(),
	)
	frappe.db.sql(
		"""
		UPDATE `tabSubcontract Compliance Line`
		SET status = 'Expiring'
		WHERE expiry_date IS NOT NULL AND expiry_date >= %s AND expiry_date <= %s AND status = 'Valid'
		""",
		(today(), add_days(today(), 30)),
	)
