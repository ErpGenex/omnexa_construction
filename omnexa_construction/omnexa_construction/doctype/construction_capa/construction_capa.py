import frappe
from frappe.model.document import Document


class ConstructionCAPA(Document):
	def validate(self):
		if self.status == "Closed" and not self.closed_date:
			self.closed_date = frappe.utils.today()
