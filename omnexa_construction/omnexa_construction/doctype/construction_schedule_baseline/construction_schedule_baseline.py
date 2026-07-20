import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate


class ConstructionScheduleBaseline(Document):
	def validate(self):
		for row in self.get("tasks") or []:
			if row.start_date and row.end_date and getdate(row.end_date) < getdate(row.start_date):
				frappe.throw(_("Task {0}: end date before start date.").format(row.task_name))
			if row.start_date and row.end_date:
				row.duration_days = date_diff(getdate(row.end_date), getdate(row.start_date)) + 1
			if row.boq_item and not row.progress_percent:
				row.progress_percent = flt(frappe.db.get_value("BOQ Item", row.boq_item, "completion_percent"))

	def on_submit(self):
		if not self.is_active:
			return
		frappe.db.set_value(
			"Project Contract",
			self.project_contract,
			{"planned_start": self.planned_start, "planned_completion": self.planned_completion
	},
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
