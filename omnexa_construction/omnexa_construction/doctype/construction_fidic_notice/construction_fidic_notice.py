import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

from omnexa_construction.fidic_compliance import refresh_fidic_notice_compliance


class ConstructionFIDICNotice(Document):
	def validate(self):
		refresh_fidic_notice_compliance(self)
		if self.response_due_date and self.status == "Open":
			if getdate(self.response_due_date) < getdate(today()):
				self.status = "Overdue"
