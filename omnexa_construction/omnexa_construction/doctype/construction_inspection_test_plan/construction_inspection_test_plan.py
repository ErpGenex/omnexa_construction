import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionInspectionTestPlan(Document):
	def validate(self):
		for row in self.lines or []:
			if row.boq_item:
				pc = frappe.db.get_value("BOQ Item", row.boq_item, "project_contract")
				if pc != self.project_contract:
					frappe.throw(_("BOQ item {0} is not on this contract.").format(row.boq_item))
				if not row.cost_code:
					row.cost_code = frappe.db.get_value("BOQ Item", row.boq_item, "cost_code")
