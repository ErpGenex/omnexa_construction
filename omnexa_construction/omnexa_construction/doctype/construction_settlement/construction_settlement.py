import frappe
from frappe.model.document import Document


class ConstructionSettlement(Document):
	def on_submit(self):
		if self.dispute_case:
			frappe.db.set_value(
				"Construction Dispute Case",
				self.dispute_case,
				{"status": "Settled", "settled_amount": self.settled_amount
	},
				update_modified=True,
			)
