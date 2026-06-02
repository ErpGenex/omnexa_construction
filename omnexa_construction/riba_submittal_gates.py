# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""RIBA stage gates linked to Engineering Submittal approvals (Phase 12.5)."""

from __future__ import annotations

import frappe
from frappe import _


APPROVED_STATUSES = frozenset({"Approved", "Rejected"})


def validate_engineering_submittal_riba_gate(doc, method=None) -> None:
	"""Block final approval unless linked RIBA Engineering Stage is active enough."""
	if doc.doctype != "Engineering Submittal":
		return
	if getattr(frappe.flags, "in_import", False) or getattr(frappe.flags, "in_patch", False):
		return
	if doc.approval_status not in APPROVED_STATUSES:
		return
	if not doc.engineering_stage:
		frappe.throw(
			_("Link a RIBA Engineering Stage before final submittal approval."),
			title=_("RIBA gate"),
		)
	if not frappe.db.exists("DocType", "Engineering Stage"):
		return

	stage = frappe.db.get_value(
		"Engineering Stage",
		doc.engineering_stage,
		["status", "stage", "consulting_unit"],
		as_dict=True,
	)
	if not stage:
		frappe.throw(_("Linked Engineering Stage not found."), title=_("RIBA gate"))

	if stage.status not in ("In Progress", "Completed"):
		frappe.throw(
			_(
				"Submittal cannot be **{0}** while RIBA stage **{1}** is **{2}**. "
				"Activate the stage (In Progress) first."
			).format(doc.approval_status, stage.stage or doc.engineering_stage, stage.status),
			title=_("RIBA gate"),
		)
