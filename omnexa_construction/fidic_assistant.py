# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""FIDIC contract assistant — clause suggestion + notice deadline (Phase 14.1)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate

from omnexa_construction.fidic_compliance import compute_notice_due_date_for_notice, time_bar_days_for_contract


@frappe.whitelist()
def suggest_fidic_clause(
	project_contract: str,
	notice_type: str | None = None,
	keywords: str | None = None,
) -> list[dict]:
	filters = {"is_active": 1}
	if notice_type:
		filters["notice_type"] = notice_type
	rows = frappe.get_all(
		"Construction FIDIC Clause Reference",
		filters=filters,
		fields=[
			"name",
			"display_reference",
			"clause_code",
			"notice_type",
			"time_bar_days",
			"title",
			"description",
		],
		limit=50,
	)
	if keywords:
		kw = keywords.lower()
		rows = [
			r
			for r in rows
			if kw in (r.title or "").lower()
			or kw in (r.description or "").lower()
			or kw in (r.clause_code or "").lower()
		]
	default_days = time_bar_days_for_contract(project_contract)
	for r in rows:
		r["suggested_notice_due"] = str(
			add_days(getdate(nowdate()), int(r.time_bar_days or default_days))
		)
		r["confidence"] = "high" if notice_type and r.notice_type == notice_type else "medium"
	return rows[:10]


@frappe.whitelist()
def draft_fidic_notice_suggestion(
	project_contract: str,
	notice_type: str,
	fidic_clause_reference: str | None = None,
	notice_date: str | None = None,
) -> dict:
	notice_date = notice_date or nowdate()
	company, branch = frappe.db.get_value(
		"Project Contract", project_contract, ["company", "branch"]
	)
	draft = frappe._dict(
		{
			"doctype": "Construction FIDIC Notice",
			"project_contract": project_contract,
			"notice_type": notice_type,
			"fidic_clause_reference": fidic_clause_reference,
			"notice_date": notice_date,
			"status": "Open",
			"company": company,
			"branch": branch,
		}
	)
	due = compute_notice_due_date_for_notice(draft)
	clause_label = None
	if fidic_clause_reference:
		clause_label = frappe.db.get_value(
			"Construction FIDIC Clause Reference",
			fidic_clause_reference,
			"display_reference",
		)
	return {
		"draft": {
			"project_contract": project_contract,
			"notice_type": notice_type,
			"fidic_clause_reference": fidic_clause_reference,
			"clause_reference": clause_label,
			"notice_date": notice_date,
			"response_due_date": str(due) if due else None,
		},
		"assistant_message": _(
			"Suggested response due by {0}. Review clause {1} before issuing notice."
		).format(due or "—", clause_label or fidic_clause_reference or "—"),
	}
