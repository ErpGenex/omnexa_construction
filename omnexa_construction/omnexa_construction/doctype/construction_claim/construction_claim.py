import frappe
from frappe import _
from frappe.model.document import Document


class ConstructionClaim(Document):
	def validate(self):
		if self.related_extension_of_time:
			pc = frappe.db.get_value(
				"Construction Extension of Time",
				self.related_extension_of_time,
				"project_contract",
			)
			if pc and pc != self.project_contract:
				frappe.throw(
					_("Related EOT must belong to the same Project Contract."),
					title=_("Claim"),
				)
		if self.related_change_order:
			pc = frappe.db.get_value(
				"Construction Change Order",
				self.related_change_order,
				"project_contract",
			)
			if pc and pc != self.project_contract:
				frappe.throw(
					_("Related change order must belong to the same Project Contract."),
					title=_("Claim"),
				)
