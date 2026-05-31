import frappe
from frappe.model.document import Document
from frappe.utils import flt, money_in_words

from omnexa_construction.construction_forms.helpers import hydrate_contract_party_fields


class ConstructionFinesStatement(Document):
	def validate(self):
		hydrate_contract_party_fields(self)
		total = 0.0
		for row in self.fines or []:
			row.total_fine = flt(row.number_of_days) * flt(row.daily_fine_amount)
			total += flt(row.total_fine)
		self.total_fines = total
		currency = frappe.db.get_value("Project Contract", self.project_contract, "contract_currency") or "EGP"
		if total and not self.total_fines_in_words:
			try:
				self.total_fines_in_words = money_in_words(total, currency)
			except Exception:
				pass
