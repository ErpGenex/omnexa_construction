# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Mock FIDIC + ISO audit scoring for World Class certification prep (Phase 15.1)."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_construction.fidic_compliance_checklist import fidic_checklist_for_contract


AUDIT_DOMAINS = (
	("FIDIC", "fidic"),
	("ISO 9001 QMS", "iso_9001"),
	("ISO 45001 HSE", "iso_45001"),
	("ISO 14001 Environment", "iso_14001"),
	("ISO 19650 CDE", "iso_19650"),
)


@frappe.whitelist()
def run_mock_audit(company: str, branch: str | None = None) -> dict:
	filters = {"company": company, "docstatus": ["<", 2]}
	if branch:
		filters["branch"] = branch
	contracts = frappe.get_all("Project Contract", filters=filters, pluck="name", limit=50)

	domains = []
	for label, key in AUDIT_DOMAINS:
		score, findings = _score_domain(key, contracts)
		domains.append({"domain": label, "key": key, "score": score, "findings": findings
	})

	overall = round(sum(d["score"] for d in domains) / max(len(domains), 1), 1)
	return {
		"company": company,
		"branch": branch,
		"contract_sample": len(contracts),
		"domains": domains,
		"overall_score": overall,
		"certification_ready": overall >= 85,
		"audit_type": "mock_internal"
	}


def _score_domain(key: str, contracts: list[str]) -> tuple[float, list[str]]:
	findings = []
	if key == "fidic":
		if not contracts:
			return 0.0, [_("No contracts in scope.")]
		rows = fidic_checklist_for_contract(contracts[0])
		passed = sum(1 for r in rows if r.get("passed"))
		score = 100 * passed / max(len(rows), 1)
		if score < 90:
			findings.append(_("FIDIC checklist below 90% on sample contract."))
		return round(score, 1), findings

	if key == "iso_9001":
		ncr_open = frappe.db.count("Construction NCR", {"status": ["!=", "Closed"], "docstatus": ["<", 2]}) if frappe.db.exists("DocType", "Construction NCR") else 0
		score = 90 if ncr_open < 10 else 75
		if ncr_open >= 10:
			findings.append(_("High open NCR count: {0}").format(ncr_open))
		return score, findings

	if key == "iso_45001":
		ptw = frappe.db.count("Construction Permit to Work", {"docstatus": ["<", 2]}) if frappe.db.exists("DocType", "Construction Permit to Work") else 0
		score = 85 if ptw else 60
		if not ptw:
			findings.append(_("No PTW records — strengthen ISO 45001 evidence."))
		return score, findings

	if key == "iso_14001":
		aspects = (
			frappe.db.count("Construction Environmental Aspect", {"docstatus": ["<", 2]})
			if frappe.db.exists("DocType", "Construction Environmental Aspect")
			else 0
		)
		waste = (
			frappe.db.count("Construction Waste Log", {"docstatus": ["<", 2]})
			if frappe.db.exists("DocType", "Construction Waste Log")
			else 0
		)
		score = 92 if aspects and waste else (80 if aspects or waste else 60)
		if not aspects:
			findings.append(_("Add Environmental Aspect register records."))
		return score, findings

	if key == "iso_19650":
		cde = frappe.db.count("Construction CDE Document", {"docstatus": ["<", 2]}) if frappe.db.exists("DocType", "Construction CDE Document") else 0
		score = 88 if cde else 55
		if cde < 5:
			findings.append(_("Limited CDE document volume."))
		return score, findings

	return 70.0, findings
