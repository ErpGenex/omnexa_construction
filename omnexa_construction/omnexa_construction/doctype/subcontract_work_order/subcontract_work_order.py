from frappe.model.document import Document
from frappe.utils import flt


class SubcontractWorkOrder(Document):
	def validate(self):
		self.amount_certified = flt(self.contract_value) * (flt(self.progress_percent) / 100.0)

