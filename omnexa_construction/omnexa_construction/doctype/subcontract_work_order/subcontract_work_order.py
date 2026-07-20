import frappe
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_construction.subcontract_financials import (
	subcontract_certified_total,
	subcontract_paid_total,
)


class SubcontractWorkOrder(Document):
	def validate(self):
		if self.name and frappe.db.exists(
			"Subcontract Payment Certificate",
			{"subcontract_work_order": self.name, "docstatus": 1
	},
		):
			certified = subcontract_certified_total(self.name)
			paid = subcontract_paid_total(self.name)
			self.amount_certified = certified
			self.amount_paid = paid
			if flt(self.contract_value):
				self.progress_percent = min(100.0, certified / flt(self.contract_value) * 100.0)
		else:
			self.amount_certified = flt(self.contract_value) * (flt(self.progress_percent) / 100.0)
