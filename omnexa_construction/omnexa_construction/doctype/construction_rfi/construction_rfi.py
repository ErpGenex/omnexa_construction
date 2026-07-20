import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ConstructionRFI(Document):
	def validate(self):
		if self.due_date and self.status == "Open" and getdate(self.due_date) < getdate(today()):
			self.status = "Overdue"
		if self.response and self.status in ("Open", "Overdue"):
			self.status = "Answered"
