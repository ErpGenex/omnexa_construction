from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt

FIDIC_CHECKLIST = [
	("notice_register", _("FIDIC notices registered with due dates")),
	("time_bar_tracking", _("Time-bar fields calculated on notices")),
	("clause_reference_kb", _("Clause reference knowledge base in use")),
	("eot_linked", _("EOT records linked to contract")),
	("claims_linked", _("Claims linked to contract")),
	("ipc_certification", _("IPC certification workflow active")),
	("retention_tracking", _("Retention held tracked on contract")),
	("performance_security", _("Performance security % defined")),
	("advance_guarantee", _("Advance payment guarantee flagged")),
	("variation_orders", _("Change orders approved and valued")),
	("final_account", _("Final account statement available")),
	("risk_register", _("Project risk register maintained")),
]


@frappe.whitelist()
def fidic_checklist_for_contract(project_contract: str) -> list[dict]:
	"""Interactive FIDIC compliance checklist with live pass/fail."""
	if not project_contract:
		return []

	contract = frappe.db.get_value(
		"Project Contract",
		project_contract,
		[
			"performance_security_percent",
			"advance_payment_guarantee",
			"retention_percent",
		],
		as_dict=True,
	) or {}

	notice_count = frappe.db.count(
		"Construction FIDIC Notice", {"project_contract": project_contract, "docstatus": ["<", 2]}
	)
	time_bar_ready = frappe.db.count(
		"Construction FIDIC Notice",
		{"project_contract": project_contract, "notice_due_date": ("is", "set")},
	)
	clause_kb = frappe.db.count("Construction FIDIC Clause Reference")
	eot_count = frappe.db.count(
		"Construction Extension of Time", {"project_contract": project_contract, "docstatus": ["<", 2]}
	)
	claim_count = frappe.db.count(
		"Construction Claim", {"project_contract": project_contract, "docstatus": ["<", 2]}
	)
	ipc_count = frappe.db.count(
		"IPC Certificate",
		{"project_contract": project_contract, "status": ("in", ("Certified", "Posted"))},
	)
	co_count = frappe.db.count(
		"Construction Change Order",
		{"project_contract": project_contract, "docstatus": 1
	},
	)
	fa_exists = frappe.db.exists(
		"Construction Final Account Statement",
		{"project_contract": project_contract, "docstatus": ["<", 2]},
	)
	risk_count = frappe.db.count(
		"Construction Project Risk", {"project_contract": project_contract, "docstatus": ["<", 2]}
	)

	checks = {
		"notice_register": notice_count > 0,
		"time_bar_tracking": notice_count == 0 or time_bar_ready > 0,
		"clause_reference_kb": clause_kb > 0,
		"eot_linked": eot_count > 0,
		"claims_linked": claim_count > 0,
		"ipc_certification": ipc_count > 0,
		"retention_tracking": flt(contract.get("retention_percent")) >= 0,
		"performance_security": flt(contract.get("performance_security_percent")) > 0,
		"advance_guarantee": bool(contract.get("advance_payment_guarantee")),
		"variation_orders": co_count > 0,
		"final_account": bool(fa_exists),
		"risk_register": risk_count > 0
	}

	out = []
	for key, label in FIDIC_CHECKLIST:
		passed = bool(checks.get(key))
		out.append({"check_id": key, "requirement": label, "passed": passed, "status": _("Pass") if passed else _("Gap")
	})
	return out
