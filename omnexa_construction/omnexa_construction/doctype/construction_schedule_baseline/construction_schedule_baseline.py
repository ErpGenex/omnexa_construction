import frappe
from frappe.model.document import Document


class ConstructionScheduleBaseline(Document):
	def on_submit(self):
		if not self.is_active:
			return
		frappe.db.set_value(
			"Project Contract",
			self.project_contract,
			{"planned_start": self.planned_start, "planned_completion": self.planned_completion},
			update_modified=True,
		)
		frappe.db.sql(
			"""
			UPDATE `tabConstruction Schedule Baseline`
			SET is_active = 0
			WHERE project_contract = %s AND name != %s AND docstatus = 1
			""",
			(self.project_contract, self.name),
		)
