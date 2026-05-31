import frappe
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_construction.contract_financials import approved_change_order_impact


class ConstructionFinalAccountStatement(Document):
	def validate(self):
		contract = frappe.db.get_value(
			"Project Contract",
			self.project_contract,
			["revised_contract_value", "contract_value", "retention_held_to_date"],
			as_dict=True,
		)
		if not contract:
			return
		self.contract_sum = flt(contract.revised_contract_value) or flt(contract.contract_value)
		self.approved_variations = approved_change_order_impact(self.project_contract)
		self.retention_held = flt(contract.retention_held_to_date)
		self.previous_certified = flt(
			frappe.db.sql(
				"""
				SELECT COALESCE(SUM(net_amount), 0)
				FROM `tabIPC Certificate`
				WHERE project_contract = %s AND docstatus = 1 AND status != 'Cancelled'
				""",
				self.project_contract,
			)[0][0]
		)
		self.gross_final_sum = self.contract_sum + flt(self.claims_allowed)
		self.final_due = self.gross_final_sum - self.retention_held - self.previous_certified
