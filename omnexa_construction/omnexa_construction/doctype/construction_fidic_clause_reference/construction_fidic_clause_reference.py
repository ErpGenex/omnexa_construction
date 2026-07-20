import frappe
from frappe.model.document import Document


class ConstructionFIDICClauseReference(Document):
	def validate(self):
		if not self.display_reference and self.clause_code and self.title:
			self.display_reference = f"{self.clause_code} — {self.title}"
		elif not self.display_reference and self.clause_code:
			self.display_reference = self.clause_code
		self.display_reference = (self.display_reference or "").strip()
		if not self.display_reference:
			frappe.throw("Display Reference is required.")
