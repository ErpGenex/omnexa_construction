import frappe
from frappe import _
from frappe.model.document import Document

from omnexa_projects_pm.wbs_integration import validate_linked_pm_wbs_task


class SiteDailyReport(Document):
	def validate(self):
		if self.boq_item:
			pc = frappe.db.get_value("BOQ Item", self.boq_item, "project_contract")
			if pc != self.project:
				frappe.throw(_("BOQ Item must belong to the same Project Contract."), title=_("Site Daily Report"))
		validate_linked_pm_wbs_task(self.project, self.pm_wbs_task)
