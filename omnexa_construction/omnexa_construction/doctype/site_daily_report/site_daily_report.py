import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_projects_pm.wbs_integration import validate_linked_pm_wbs_task


class SiteDailyReport(Document):
	def validate(self):
		for row in self.get("daily_quantities") or []:
			if row.boq_item:
				pc = frappe.db.get_value("BOQ Item", row.boq_item, "project_contract")
				if pc != self.project:
					frappe.throw(
						_("BOQ line {0} must belong to this contract.").format(row.boq_item),
						title=_("Site Daily Report"),
					)
				if not row.cost_code:
					row.cost_code = frappe.db.get_value("BOQ Item", row.boq_item, "cost_code")
				if not row.description:
					row.description = frappe.db.get_value("BOQ Item", row.boq_item, "item_description")
				if not row.unit_of_measure:
					row.unit_of_measure = frappe.db.get_value("BOQ Item", row.boq_item, "unit_of_measure")
			row.quantity_done = flt(row.quantity_done)
		if self.boq_item:
			pc = frappe.db.get_value("BOQ Item", self.boq_item, "project_contract")
			if pc != self.project:
				frappe.throw(_("BOQ Item must belong to the same Project Contract."), title=_("Site Daily Report"))
		validate_linked_pm_wbs_task(self.project, self.pm_wbs_task)
