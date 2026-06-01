import frappe
from frappe.model.document import Document
from frappe.utils import flt


def compute_retention_release(retention_amount: float, release_percent: float) -> float:
	return flt(retention_amount) * flt(release_percent) / 100


class SubcontractRetentionRelease(Document):
	def validate(self):
		self.net_release = compute_retention_release(self.retention_amount, self.release_percent)
