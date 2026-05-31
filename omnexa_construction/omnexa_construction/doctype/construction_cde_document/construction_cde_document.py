import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionCDEDocument(Document):
	def validate(self):
		if self.approval_status == "Superseded" and not self.superseded_by:
			frappe.msgprint(_("Link the replacing revision in Superseded By."), indicator="orange")

	def on_update(self):
		if self.approval_status != "Approved" or not self.document_number:
			return
		previous = frappe.get_all(
			"Construction CDE Document",
			filters={
				"project_contract": self.project_contract,
				"document_number": self.document_number,
				"name": ["!=", self.name],
				"approval_status": ["!=", "Superseded"],
			},
			pluck="name",
		)
		for name in previous:
			frappe.db.set_value(
				"Construction CDE Document",
				name,
				{"approval_status": "Superseded", "superseded_by": self.name, "cde_status": "Archived"},
				update_modified=True,
			)
