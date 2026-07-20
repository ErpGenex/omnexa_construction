# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Liquidated damages (LD) calculation and IPC deduction helpers."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate


def calc_delay_days(scheduled_finish, actual_finish) -> int:
	if not scheduled_finish or not actual_finish:
		return 0
	from frappe.utils import date_diff

	return max(0, date_diff(getdate(actual_finish), getdate(scheduled_finish)))


def get_contract_ld_rates(project_contract: str) -> dict:
	row = frappe.db.get_value(
		"Project Contract",
		project_contract,
		["liquidated_damages_per_day", "liquidated_damages_cap_percent", "revised_contract_value", "contract_value"],
		as_dict=True,
	)
	if not row:
		return {"ld_per_day": 0.0, "ld_cap": 0.0, "contract_value": 0.0
	}
	contract_value = flt(row.revised_contract_value) or flt(row.contract_value)
	cap_pct = flt(row.liquidated_damages_cap_percent) or 10.0
	return {
		"ld_per_day": flt(row.liquidated_damages_per_day),
		"ld_cap": contract_value * cap_pct / 100.0 if contract_value else 0.0,
		"contract_value": contract_value
	}


def calc_ld_amount(
	project_contract: str,
	delay_days: int,
	*,
	amount_override: float | None = None,
) -> dict:
	"""Return LD amount capped by contract LD cap."""
	rates = get_contract_ld_rates(project_contract)
	days = int(delay_days or 0)
	if amount_override is not None:
		raw = flt(amount_override)
	else:
		raw = rates["ld_per_day"] * days
	cap = rates["ld_cap"]
	amount = min(raw, cap) if cap else raw
	return {
		"delay_days": days,
		"ld_per_day": rates["ld_per_day"],
		"ld_cap": cap,
		"raw_amount": raw,
		"ld_amount": max(0.0, amount)}


def sum_fines_for_contract(project_contract: str, to_date=None) -> float:
	if not frappe.db.exists("DocType", "Construction Fines Statement"):
		return 0.0
	filters = {"project_contract": project_contract, "docstatus": 1
	}
	if to_date:
		filters["to_date"] = ["<=", to_date]
	names = frappe.get_all("Construction Fines Statement", filters=filters, pluck="name")
	if not names:
		return 0.0
	return flt(
		frappe.db.sql(
			"""
			SELECT COALESCE(SUM(total_fines), 0)
			FROM `tabConstruction Fines Statement`
			WHERE name IN %(names)s
			""",
			{"names": names
	},
		)[0][0]
	)


def sum_delay_ld_for_contract(project_contract: str, *, contractor_attributable_only: bool = True) -> float:
	if not frappe.db.exists("DocType", "Construction Work Delay Notice"):
		return 0.0
	filters = {"project_contract": project_contract, "docstatus": 1
	}
	if contractor_attributable_only:
		filters["reason_contractor"] = 1
	total = 0.0
	for row in frappe.get_all(
		"Construction Work Delay Notice",
		filters=filters,
		fields=["estimated_ld_amount"],
	):
		total += flt(row.estimated_ld_amount)
	return total


def build_ipc_deduction_summary(ipc_doc) -> dict:
	"""Aggregate penalty sources for an IPC period."""
	project_contract = ipc_doc.project_contract
	period_to = ipc_doc.get("period_to") or ipc_doc.get("ipc_date")
	fines = sum_fines_for_contract(project_contract, period_to)
	delay_ld = sum_delay_ld_for_contract(project_contract)
	manual_penalty = flt(ipc_doc.get("penalty_deduction"))
	other = flt(ipc_doc.get("other_deductions"))
	suggested_penalty = fines + delay_ld
	notes = []
	if fines:
		notes.append(_("Fines statements: {0}").format(frappe.format(fines, {"fieldtype": "Currency"
	})))
	if delay_ld:
		notes.append(_("Contractor delay LD (submitted notices): {0}").format(frappe.format(delay_ld, {"fieldtype": "Currency"
	})))
	return {
		"fines_total": fines,
		"delay_ld_total": delay_ld,
		"suggested_penalty": suggested_penalty,
		"manual_penalty": manual_penalty,
		"other_deductions": other,
		"ld_calculation_notes": "\n".join(notes) if notes else ""
	}


@frappe.whitelist()
def apply_deductions_to_ipc(ipc_name: str, *, use_suggested: bool = True) -> dict:
	doc = frappe.get_doc("IPC Certificate", ipc_name)
	if doc.docstatus == 1:
		frappe.throw(_("Cannot recalculate deductions on a submitted IPC."), title=_("IPC"))
	summary = build_ipc_deduction_summary(doc)
	if use_suggested and doc.meta.has_field("penalty_deduction"):
		doc.penalty_deduction = summary["suggested_penalty"]
	if doc.meta.has_field("ld_calculation_notes"):
		doc.ld_calculation_notes = summary["ld_calculation_notes"]
	doc.validate()
	doc.save()
	return summary
