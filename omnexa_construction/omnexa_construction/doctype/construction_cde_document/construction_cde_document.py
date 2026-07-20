import frappe
from frappe import _
from frappe.model.document import Document

from omnexa_construction.cde_transmittal import maybe_create_transmittal_for_published_cde
from omnexa_construction.cde_workflow import user_can_publish_cde, validate_cde_status_transition


class ConstructionCDEDocument(Document):
	def validate(self):
		if not self.is_new():
			old_status = frappe.db.get_value(self.doctype, self.name, "cde_status")
			validate_cde_status_transition(old_status, self.cde_status)
		if self.cde_status == "Published" and not user_can_publish_cde():
			frappe.throw(_("Only Document Controller / Project Manager can publish CDE documents."), title=_("CDE"))
		if self.approval_status == "Superseded" and not self.superseded_by:
			frappe.msgprint(_("Link the replacing revision in Superseded By."), indicator="orange")

	def on_update(self):
		if self.cde_status == "Published":
			maybe_create_transmittal_for_published_cde(self)
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
