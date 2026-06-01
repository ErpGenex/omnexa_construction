import frappe
from frappe.model.document import Document

from omnexa_construction.contract_financials import refresh_project_contract_financials


class ConstructionChangeOrder(Document):
	def validate(self):
		if not self.project_contract:
			return
		from omnexa_construction.change_order_boq import compute_boq_line_amounts

		compute_boq_line_amounts(self)
		if self.is_new() or self.has_value_changed("status") or self.has_value_changed("cost_impact"):
			refresh_project_contract_financials(self.project_contract)

	def on_update(self):
		if self.status == "Implemented" and self.docstatus == 1:
			from omnexa_construction.change_order_boq import apply_change_order_to_boq

			apply_change_order_to_boq(self)

	def on_trash(self):
		if self.project_contract:
			refresh_project_contract_financials(self.project_contract)
