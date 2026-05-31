import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionNCR(Document):
	def validate(self):
		if self.boq_item:
			pc = frappe.db.get_value("BOQ Item", self.boq_item, "project_contract")
			if pc != self.project_contract:
				frappe.throw(_("BOQ Item must belong to the same Project Contract."), title=_("NCR"))
