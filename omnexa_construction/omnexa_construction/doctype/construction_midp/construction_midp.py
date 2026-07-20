import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ConstructionMIDP(Document):
	def validate(self):
		for row in self.lines or []:
			if row.planned_issue_date and getdate(row.planned_issue_date) < getdate(today()) and row.status == "Planned":
				row.status = "Overdue"
