import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionExtensionofTime(Document):
	def validate(self):
		if self.related_change_order:
			co_pc = frappe.db.get_value("Construction Change Order", self.related_change_order, "project_contract")
			if co_pc and co_pc != self.project_contract:
				frappe.throw(
					_("Related Change Order must belong to the same Project Contract."),
					title=_("EOT"),
				)
