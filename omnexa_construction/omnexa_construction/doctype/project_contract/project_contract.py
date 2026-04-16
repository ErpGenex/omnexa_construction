import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_construction.contract_financials import (
	approved_change_order_impact,
	retention_held_from_certified_ipc,
)
from omnexa_projects_pm.wbs_integration import validate_linked_pm_wbs_task


class ProjectContract(Document):
	def validate(self):
		validate_linked_pm_wbs_task(self.name, self.primary_wbs_task, label="Primary WBS Task")
		if self.planned_start and self.planned_completion and self.planned_completion < self.planned_start:
			frappe.throw(_("Planned Completion cannot be before Planned Start."), title=_("Schedule"))
		co = approved_change_order_impact(self.name)
		self.approved_change_orders_value = co
		self.revised_contract_value = flt(self.contract_value) + co
		self.retention_held_to_date = retention_held_from_certified_ipc(self.name)
