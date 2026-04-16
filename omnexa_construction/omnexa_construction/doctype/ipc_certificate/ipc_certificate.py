import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime

from omnexa_construction.contract_financials import billable_contract_value
from omnexa_construction.ipc_billing import compute_ipc_amounts
from omnexa_projects_pm.wbs_integration import validate_linked_pm_wbs_task


def _prior_certified_completion_percent(
	project_contract: str,
	exclude_name: str | None,
	ipc_date,
	creation_anchor,
) -> float:
	row = frappe.db.sql(
		"""
		SELECT boq_completion_percent
		FROM `tabIPC Certificate`
		WHERE project_contract = %s
			AND COALESCE(name, '') != COALESCE(%s, '')
			AND status IN ('Certified', 'Posted')
			AND docstatus < 2
			AND (
				ipc_date < %s
				OR (ipc_date = %s AND creation < %s)
			)
		ORDER BY ipc_date DESC, creation DESC
		LIMIT 1
		""",
		(project_contract, exclude_name or "", ipc_date, ipc_date, creation_anchor),
	)
	return flt(row[0][0]) if row else 0.0


class IPCCertificate(Document):
	def validate(self):
		if not self.project_contract:
			return

		contract = frappe.get_doc("Project Contract", self.project_contract)
		self.company = self.company or contract.company
		self.branch = self.branch or contract.branch

		billable = billable_contract_value(self.project_contract)
		self.billable_contract_value = billable

		anchor = self.creation or now_datetime()
		prior_pct = _prior_certified_completion_percent(
			self.project_contract,
			self.name,
			self.ipc_date,
			anchor,
		)
		cur_pct = flt(self.boq_completion_percent)
		if cur_pct < prior_pct:
			frappe.throw(
				_("Cumulative BOQ completion % ({0}%) cannot be below the last certified IPC ({1}%).").format(
					cur_pct, prior_pct
				),
				title=_("IPC"),
			)

		retention_pct = flt(
			frappe.db.get_value("Project Contract", self.project_contract, "retention_percent")
		)
		out = compute_ipc_amounts(
			billable_contract_value=billable,
			cumulative_completion_percent=cur_pct,
			prior_certified_completion_percent=prior_pct,
			retention_percent=retention_pct,
			advance_recovery=flt(self.advance_recovery),
		)
		self.prior_cumulative_billed = out["prior_cumulative_billed"]
		self.cumulative_value_billed = out["cumulative_value_billed"]
		self.gross_amount = out["gross_amount"]
		self.retention_deduction = out["retention_deduction"]
		self.net_amount = out["net_amount"]

		validate_linked_pm_wbs_task(self.project_contract, self.pm_wbs_task)
		self._validate_boq_lines()

	def _validate_boq_lines(self):
		rows = [r for r in self.get("boq_lines") or [] if getattr(r, "boq_item", None)]
		if not rows:
			return
		gross = flt(self.gross_amount)
		total = 0.0
		for r in rows:
			pc = frappe.db.get_value("BOQ Item", r.boq_item, "project_contract")
			if pc != self.project_contract:
				frappe.throw(
					_("BOQ Item {0} does not belong to this Project Contract.").format(r.boq_item),
					title=_("IPC"),
				)
			desc, sec = frappe.db.get_value(
				"BOQ Item", r.boq_item, ["item_description", "section_name"]
			)
			r.item_description = desc or ""
			r.section_name = sec or ""
			total += flt(r.period_value)
		tol = max(1.0, abs(gross) * 0.005)
		if abs(total - gross) > tol:
			frappe.throw(
				_("BOQ line period values total {0} must match Period Gross Amount {1} (tolerance {2}).").format(
					round(total, 2),
					round(gross, 2),
					round(tol, 2),
				),
				title=_("IPC"),
			)
