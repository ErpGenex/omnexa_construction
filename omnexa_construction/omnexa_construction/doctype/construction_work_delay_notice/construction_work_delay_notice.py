import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate


class ConstructionWorkDelayNotice(Document):
	def validate(self):
		if self.scheduled_finish_date and self.actual_finish_date:
			self.delay_days = max(
				0,
				date_diff(getdate(self.actual_finish_date), getdate(self.scheduled_finish_date)),
			)
		if self.boq_item and self.project_contract:
			pc = frappe.db.get_value("BOQ Item", self.boq_item, "project_contract")
			if pc != self.project_contract:
				frappe.throw(frappe._("BOQ item is not on this contract."))
		ld_day = flt(
			frappe.db.get_value("Project Contract", self.project_contract, "liquidated_damages_per_day")
		)
		if self.reason_contractor and self.delay_days and ld_day:
			cap_pct = flt(
				frappe.db.get_value("Project Contract", self.project_contract, "liquidated_damages_cap_percent")
			) or 10
			contract_value = flt(
				frappe.db.get_value("Project Contract", self.project_contract, "revised_contract_value")
			) or flt(frappe.db.get_value("Project Contract", self.project_contract, "contract_value"))
			raw = ld_day * flt(self.delay_days)
			cap = contract_value * cap_pct / 100.0 if contract_value else raw
			self.estimated_ld_amount = min(raw, cap) if cap else raw
		elif hasattr(self, "estimated_ld_amount"):
			self.estimated_ld_amount = 0
