import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ConstructionEquipmentUsage(Document):
	def validate(self):
		if self.boq_item:
			pc = frappe.db.get_value("BOQ Item", self.boq_item, "project_contract")
			if pc != self.project_contract:
				frappe.throw(_("BOQ item does not belong to this contract."), title=_("Equipment Usage"))
		self.total_cost = flt(self.hours) * flt(self.hourly_rate)
