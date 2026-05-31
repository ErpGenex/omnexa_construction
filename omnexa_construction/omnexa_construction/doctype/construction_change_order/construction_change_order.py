import frappe
from frappe.model.document import Document

from omnexa_construction.contract_financials import refresh_project_contract_financials


class ConstructionChangeOrder(Document):
	def validate(self):
		if not self.project_contract:
			return
		if self.is_new() or self.has_value_changed("status") or self.has_value_changed("cost_impact"):
			refresh_project_contract_financials(self.project_contract)

	def on_trash(self):
		if self.project_contract:
			refresh_project_contract_financials(self.project_contract)
