import frappe
from frappe.model.document import Document


class ConstructionDABReferral(Document):
	def on_submit(self):
		if self.dispute_case:
			frappe.db.set_value(
				"Construction Dispute Case",
				self.dispute_case,
				{"status": "DAB Referral"
	},
				update_modified=True,
			)
