import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, today


class ConstructionDLPRecord(Document):
	def validate(self):
		months = self.dlp_months
		if not months and self.project_contract:
			months = frappe.db.get_value(
				"Project Contract", self.project_contract, "defects_liability_months"
			)
		self.dlp_months = int(months or 12)
		if self.handover_date:
			self.dlp_end_date = add_months(getdate(self.handover_date), self.dlp_months)
		if self.dlp_end_date and getdate(self.dlp_end_date) < getdate(today()) and self.status == "Active":
			self.status = "Expired"
