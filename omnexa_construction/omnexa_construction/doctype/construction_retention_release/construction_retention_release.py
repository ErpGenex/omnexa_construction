import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionRetentionRelease(Document):
	def validate(self):
		if self.project_contract and self.release_amount:
			held = frappe.db.get_value("Project Contract", self.project_contract, "retention_held_to_date") or 0
			if frappe.utils.flt(self.release_amount) > frappe.utils.flt(held) and held:
				frappe.msgprint(
					_("Release amount exceeds retention held on contract ({0}).").format(held),
					indicator="orange",
				)
