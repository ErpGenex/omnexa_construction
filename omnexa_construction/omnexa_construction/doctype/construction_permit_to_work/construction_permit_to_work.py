import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class ConstructionPermittoWork(Document):
	def validate(self):
		if self.valid_from and self.valid_to:
			if get_datetime(self.valid_to) < get_datetime(self.valid_from):
				frappe.throw(_("Valid To must be after Valid From."))
		if self.status == "Active" and self.valid_to and get_datetime(self.valid_to) < now_datetime():
			self.status = "Expired"
