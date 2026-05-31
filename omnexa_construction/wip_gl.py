from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, getdate, today

from omnexa_construction.contract_financials import certified_ipc_net_total
from omnexa_construction.evm_metrics import actual_cost_from_boq


@frappe.whitelist()
def create_wip_snapshot_from_project(
	project_contract: str,
	snapshot_date: str | None = None,
	*,
	update_existing: int = 0,
) -> dict:
	"""Create WIP snapshot from BOQ actual cost and certified IPC revenue."""
	if not project_contract or not frappe.db.exists("Project Contract", project_contract):
		frappe.throw(_("Project Contract is required."), title=_("WIP"))

	as_of = getdate(snapshot_date or today())
	contract = frappe.db.get_value(
		"Project Contract",
		project_contract,
		["company", "branch", "contract_title"],
		as_dict=True,
	)
	cost = actual_cost_from_boq(project_contract)
	revenue = certified_ipc_net_total(project_contract)
	gl_cost, gl_revenue = _gl_totals_if_available(project_contract, contract.company, as_of)
	if gl_cost:
		cost = gl_cost
	if gl_revenue:
		revenue = gl_revenue

	existing = frappe.db.exists(
		"Project WIP Snapshot",
		{"project_contract": project_contract, "snapshot_date": as_of},
	)
	if existing and not int(update_existing):
		doc = frappe.get_doc("Project WIP Snapshot", existing)
		return {"name": doc.name, "updated": False, "wip_balance": doc.wip_balance}

	payload = {
		"doctype": "Project WIP Snapshot",
		"project_contract": project_contract,
		"snapshot_date": as_of,
		"cost_to_date": cost,
		"revenue_recognized": revenue,
		"company": contract.company,
		"branch": contract.branch,
		"snapshot_reference": _("Auto from BOQ/IPC/GL"),
	}
	if existing:
		doc = frappe.get_doc("Project WIP Snapshot", existing)
		doc.update(payload)
		doc.flags.ignore_permissions = True
		doc.save()
	else:
		doc = frappe.get_doc(payload)
		doc.flags.ignore_permissions = True
		doc.insert()

	return {
		"name": doc.name,
		"updated": True,
		"cost_to_date": cost,
		"revenue_recognized": revenue,
		"wip_balance": doc.wip_balance,
	}


def _gl_totals_if_available(project_contract: str, company: str, as_of) -> tuple[float, float]:
	"""Optional GL bridge when Journal Entry has project_contract custom field."""
	if not frappe.db.exists("DocType", "Journal Entry"):
		return 0.0, 0.0
	je_meta = frappe.get_meta("Journal Entry")
	if not je_meta.has_field("project_contract"):
		return 0.0, 0.0
	cost_accounts = frappe.get_all(
		"Account",
		filters={"company": company, "root_type": "Expense", "is_group": 0},
		pluck="name",
		limit=50,
	)
	income_accounts = frappe.get_all(
		"Account",
		filters={"company": company, "root_type": "Income", "is_group": 0},
		pluck="name",
		limit=50,
	)
	if not cost_accounts and not income_accounts:
		return 0.0, 0.0
	cost = income = 0.0
	if cost_accounts:
		cost = flt(
			frappe.db.sql(
				"""
				SELECT COALESCE(SUM(jea.debit - jea.credit), 0)
				FROM `tabJournal Entry Account` jea
				INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
				WHERE je.docstatus = 1
					AND je.project_contract = %s
					AND je.posting_date <= %s
					AND jea.account IN ({})
				""".format(", ".join(["%s"] * len(cost_accounts))),
				[project_contract, as_of, *cost_accounts],
			)[0][0]
		)
	if income_accounts:
		income = flt(
			frappe.db.sql(
				"""
				SELECT COALESCE(SUM(jea.credit - jea.debit), 0)
				FROM `tabJournal Entry Account` jea
				INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
				WHERE je.docstatus = 1
					AND je.project_contract = %s
					AND je.posting_date <= %s
					AND jea.account IN ({})
				""".format(", ".join(["%s"] * len(income_accounts))),
				[project_contract, as_of, *income_accounts],
			)[0][0]
		)
	return cost, income
