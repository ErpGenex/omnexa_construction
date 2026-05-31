import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ConstructionFIDICNotice(Document):
	def validate(self):
		if self.response_due_date and self.status == "Open":
			if getdate(self.response_due_date) < getdate(today()):
				self.status = "Overdue"
