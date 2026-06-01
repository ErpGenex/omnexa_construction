import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class ConstructionSupplierPrequalification(Document):
	def validate(self):
		if self.expiry_date and self.evaluation_date and getdate(self.expiry_date) < getdate(self.evaluation_date):
			frappe.throw(_("Expiry date cannot be before evaluation date."), title=_("Prequalification"))

	def on_submit(self):
		if self.status == "Pending":
			self.db_set("status", "Approved", update_modified=False)
