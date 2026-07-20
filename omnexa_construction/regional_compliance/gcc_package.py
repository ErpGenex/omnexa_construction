# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""GCC compliance package — ZATCA/e-invoice hooks, Arabic forms, LD (Phase 13.1)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


GCC_COUNTRIES = frozenset({"SA", "AE", "QA", "KW", "BH", "OM"})


@frappe.whitelist()
def get_gcc_compliance_snapshot(project_contract: str) -> dict:
	fields = ["company", "branch", "governing_standard"]
	meta = frappe.get_meta("Project Contract")
	if meta.has_field("liquidated_damages_rate"):
		fields.append("liquidated_damages_rate")
	contract = frappe.db.get_value("Project Contract", project_contract, fields, as_dict=True)
	if not contract:
		frappe.throw(_("Project Contract not found."), title=_("GCC Package"))

	country = _branch_country(contract.branch)
	checks = [
		{
			"id": "arabic_forms",
			"label": _("Arabic print formats available"),
			"status": "pass" if _has_arabic_prints() else "warn",
		},
		{
			"id": "zatca",
			"label": _("ZATCA / e-invoice branch configuration"),
			"status": "pass" if _zatca_ready(contract.branch, country) else "na",
			"detail": country or "",
		},
		{
			"id": "ld",
			"label": _("Liquidated damages on contract"),
			"status": "pass" if flt(getattr(contract, "liquidated_damages_rate", None)) > 0 else "warn",
		},
		{
			"id": "fidic",
			"label": _("FIDIC governing standard"),
			"status": "pass" if "fidic" in (contract.governing_standard or "").lower() else "info",
		},
	]
	passed = sum(1 for c in checks if c["status"] == "pass")
	return {
		"package": "GCC",
		"project_contract": project_contract,
		"country": country,
		"checks": checks,
		"score_percent": round(100 * passed / max(len(checks), 1), 1),
	}


def _branch_country(branch: str | None) -> str | None:
	if not branch or not frappe.db.exists("DocType", "Branch"):
		return None
	meta = frappe.get_meta("Branch")
	for fieldname in ("country", "custom_country"):
		if meta.has_field(fieldname):
			val = frappe.db.get_value("Branch", branch, fieldname)
			if val:
				return val
	return None


def _zatca_ready(branch: str | None, country: str | None) -> bool:
	if country != "SA":
		return False
	if not branch or not frappe.db.exists("DocType", "Branch"):
		return False
	meta = frappe.get_meta("Branch")
	if meta.has_field("enable_zatca_e_invoicing"):
		return bool(frappe.db.get_value("Branch", branch, "enable_zatca_e_invoicing"))
	return False


def _has_arabic_prints() -> bool:
	return bool(
		frappe.db.count(
			"Print Format",
			{"module": "Omnexa Construction", "disabled": 0},
		)
	)
