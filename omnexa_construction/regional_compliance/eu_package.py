# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""EU compliance package — GDPR CDE access logs, CE marking refs (Phase 13.2)."""

from __future__ import annotations

import frappe
from frappe import _


EU_COUNTRIES = frozenset(
	{
		"AT",
		"BE",
		"BG",
		"HR",
		"CY",
		"CZ",
		"DK",
		"EE",
		"FI",
		"FR",
		"DE",
		"GR",
		"HU",
		"IE",
		"IT",
		"LV",
		"LT",
		"LU",
		"MT",
		"NL",
		"PL",
		"PT",
		"RO",
		"SK",
		"SI",
		"ES",
		"SE",
	}
)


def log_cde_access_on_load(doc, method=None) -> None:
	if not doc.name or doc.is_new():
		return
	if frappe.flags.in_import or frappe.flags.in_patch:
		return
	try:
		log_cde_document_access(doc.name, action="view")
	except Exception:
		pass


@frappe.whitelist()
def log_cde_document_access(cde_document: str, action: str = "view") -> dict:
	if not frappe.db.exists("DocType", "Construction CDE Access Log"):
		return {"logged": False, "reason": "doctype_missing"
	}
	if not frappe.db.exists("Construction CDE Document", cde_document):
		frappe.throw(_("CDE document not found."), title=_("GDPR log"))

	doc = frappe.get_doc("Construction CDE Document", cde_document)
	log = frappe.get_doc(
		{
			"doctype": "Construction CDE Access Log",
			"cde_document": cde_document,
			"project_contract": doc.project_contract,
			"user": frappe.session.user,
			"action": action,
			"company": doc.company,
			"branch": doc.branch
	}
	)
	log.insert(ignore_permissions=True)
	return {"logged": True, "name": log.name
	}


@frappe.whitelist()
def get_eu_compliance_snapshot(project_contract: str) -> dict:
	access_logs = 0
	if frappe.db.exists("DocType", "Construction CDE Access Log"):
		access_logs = frappe.db.count(
			"Construction CDE Access Log", {"project_contract": project_contract
	}
		)
	cde_count = frappe.db.count(
		"Construction CDE Document",
		{"project_contract": project_contract, "docstatus": ["<", 2]},
	)
	ce_filters = {"project_contract": project_contract, "docstatus": ["<", 2]}
	meta = frappe.get_meta("Construction CDE Document")
	if meta.has_field("document_type"):
		ce_filters["document_type"] = ["in", ["Product Declaration", "Technical Submittal"]]
	ce_refs = frappe.db.count("Construction CDE Document", ce_filters)
	checks = [
		{
			"id": "gdpr_log",
			"label": _("CDE access audit trail (GDPR)"),
			"status": "pass" if access_logs or not cde_count else "warn",
			"detail": _("{0} log entries").format(access_logs)
	},
		{
			"id": "ce_refs",
			"label": _("CE / product declaration documents"),
			"status": "pass" if ce_refs else "info",
			"detail": _("{0} documents").format(ce_refs)
	},
	]
	return {
		"package": "EU",
		"project_contract": project_contract,
		"checks": checks,
		"score_percent": round(100 * sum(1 for c in checks if c["status"] == "pass") / len(checks), 1)}
