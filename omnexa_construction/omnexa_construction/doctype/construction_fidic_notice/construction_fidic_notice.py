import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

from omnexa_construction.fidic_compliance import refresh_fidic_notice_compliance


class ConstructionFIDICNotice(Document):
	def validate(self):
		if not self.fidic_clause_reference and self.notice_type:
			# Non-breaking default: suggest first matching reference by notice_type
			self.fidic_clause_reference = frappe.db.get_value(
				"Construction FIDIC Clause Reference",
				{"notice_type": self.notice_type, "standard_family": ["in", ["FIDIC", "NEC4", "Other / Bespoke"]]},
				"name",
			)
		if self.fidic_clause_reference and not self.clause_reference:
			self.clause_reference = frappe.db.get_value(
				"Construction FIDIC Clause Reference", self.fidic_clause_reference, "display_reference"
			) or frappe.db.get_value(
				"Construction FIDIC Clause Reference", self.fidic_clause_reference, "clause_code"
			)
		refresh_fidic_notice_compliance(self)
		if self.response_due_date and self.status == "Open":
			if getdate(self.response_due_date) < getdate(today()):
				self.status = "Overdue"
