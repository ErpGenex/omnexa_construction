import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_projects_pm.wbs_integration import (
	recompute_pm_wbs_progress_from_boq,
	validate_linked_pm_wbs_task,
)


class BOQItem(Document):
	def validate(self):
		self._validate_boq_hierarchy()
		if self.is_group:
			children = frappe.get_all(
				"BOQ Item",
				filters={"parent_boq_item": self.name, "docstatus": ["<", 2]},
				fields=["planned_cost"],
			)
			self.planned_cost = sum(flt(r.planned_cost) for r in children)
		else:
			unit_cost = flt(self.unit_cost)
			self.planned_cost = flt(self.quantity) * unit_cost
		validate_linked_pm_wbs_task(self.project_contract, self.pm_wbs_task)
		self._warn_cost_overrun()

	def _warn_cost_overrun(self):
		if self.is_group:
			return
		planned = flt(self.planned_cost)
		actual = flt(self.actual_cost)
		if planned > 0 and actual > planned:
			frappe.msgprint(
				_("Actual cost exceeds planned cost for this BOQ line."),
				indicator="orange",
				title=_("Cost overrun"),
			)

	def _validate_boq_hierarchy(self):
		if not self.parent_boq_item:
			return
		if self.parent_boq_item == self.name:
			frappe.throw(_("Parent BOQ Item cannot be this line itself."), title=_("BOQ"))
		parent_pc = frappe.db.get_value("BOQ Item", self.parent_boq_item, "project_contract")
		if parent_pc != self.project_contract:
			frappe.throw(_("Parent BOQ must belong to the same Project Contract."), title=_("BOQ"))
		depth = 0
		walk = self.parent_boq_item
		while walk:
			depth += 1
			if depth > 30:
				frappe.throw(_("BOQ hierarchy is too deep."), title=_("BOQ"))
			if walk == self.name:
				frappe.throw(_("Circular BOQ parent reference."), title=_("BOQ"))
			walk = frappe.db.get_value("BOQ Item", walk, "parent_boq_item")

	def after_insert(self):
		if self.pm_wbs_task:
			recompute_pm_wbs_progress_from_boq(self.pm_wbs_task)
		self._rollup_parent_planned_cost()

	def on_update(self):
		old = self.get_doc_before_save()
		old_task = getattr(old, "pm_wbs_task", None) if old else None
		for task in {t for t in (old_task, self.pm_wbs_task) if t}:
			recompute_pm_wbs_progress_from_boq(task)
		self._rollup_parent_planned_cost()

	def on_trash(self):
		if self.pm_wbs_task:
			recompute_pm_wbs_progress_from_boq(self.pm_wbs_task, exclude_boq=self.name)
		if self.parent_boq_item:
			self._rollup_parent_planned_cost(parent_name=self.parent_boq_item)

	def _rollup_parent_planned_cost(self, parent_name: str | None = None):
		parent = parent_name or self.parent_boq_item
		if not parent or not frappe.db.exists("BOQ Item", parent):
			return
		if not frappe.db.get_value("BOQ Item", parent, "is_group"):
			return
		children = frappe.get_all(
			"BOQ Item",
			filters={"parent_boq_item": parent, "docstatus": ["<", 2]},
			fields=["planned_cost"],
		)
		total = sum(flt(r.planned_cost) for r in children)
		frappe.db.set_value("BOQ Item", parent, "planned_cost", total, update_modified=False)
