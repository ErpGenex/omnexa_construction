from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_construction.construction_forms.helpers import hydrate_contract_party_fields


class ContractorAccountStatement(Document):
	def validate(self):
		hydrate_contract_party_fields(self)
		self._rollup_totals()

	def _rollup_totals(self) -> None:
		exec_total = pay_total = debit_total = credit_total = 0.0
		for row in self.lines or []:
			exec_total += flt(row.executed_works_value)
			pay_total += flt(row.prior_payments)
			debit_total += flt(row.debit_balance)
			credit_total += flt(row.credit_balance)
		self.total_executed_works = exec_total
		self.total_prior_payments = pay_total
		self.debit_balance_due_contractor = debit_total
		self.credit_balance_due_from_contractor = credit_total


@frappe.whitelist()
def load_lines_from_ipc(statement_name: str) -> dict:
	doc = frappe.get_doc("Contractor Account Statement", statement_name)
	if not doc.project_contract:
		frappe.throw(_("Project Contract is required."), title=_("Account Statement"))
	ipcs = frappe.get_all(
		"IPC Certificate",
		filters={
			"project_contract": doc.project_contract,
			"status": ["in", ["Certified", "Posted"]],
			"docstatus": ["<", 2],
		},
		fields=["name", "ipc_date", "cumulative_value_billed", "net_amount", "certificate_reference"],
		order_by="ipc_date asc, creation asc",
	)
	doc.set("lines", [])
	running_paid = 0.0
	for i, ipc in enumerate(ipcs, start=1):
		if doc.to_date and str(ipc.ipc_date) > str(doc.to_date):
			break
		net = flt(ipc.net_amount)
		doc.append(
			"lines",
			{
				"idx": i,
				"description": _("IPC No. {0}").format(i),
				"ipc_certificate": ipc.name,
				"ipc_date": ipc.ipc_date,
				"executed_works_value": flt(ipc.cumulative_value_billed),
				"prior_payments": running_paid,
				"debit_balance": net,
				"credit_balance": 0,
				"remarks": ipc.certificate_reference or "",
			},
		)
		running_paid += net
	doc.flags.ignore_permissions = True
	doc.save()
	return {"lines": len(doc.lines)}
