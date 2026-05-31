from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from omnexa_construction.wizard.pricing import recalculate_setup_pricing


class ConstructionProjectSetup(Document):
	def validate(self):
		if self.status not in ("Completed", "Failed"):
			recalculate_setup_pricing(self)
		if getattr(self.flags, "wizard_save", False):
			return
		self._validate_phases()
		self._validate_ipc_plan()

	def _validate_phases(self):
		total = sum(flt(p.weight_percent) for p in (self.phases or []))
		if self.phases and abs(total - 100.0) > 0.05:
			frappe.msgprint(
				_("Phase weights total {0}% (should be 100%).").format(total),
				indicator="orange",
				title=_("Phases"),
			)

	def _validate_ipc_plan(self):
		prior = 0.0
		for row in sorted(self.ipc_plan or [], key=lambda r: int(r.ipc_number or 0)):
			cur = flt(row.cumulative_completion_percent)
			if cur < prior:
				frappe.throw(
					_("IPC #{0}: cumulative % ({1}) cannot be below prior IPC ({2}%).").format(
						row.ipc_number, cur, prior
					),
					title=_("IPC Plan"),
				)
			prior = cur
		if prior > 100.01:
			frappe.throw(_("IPC cumulative completion cannot exceed 100%."), title=_("IPC Plan"))

	def before_save(self):
		if self.status == "Draft" and self.wizard_step and self.wizard_step > 1:
			self.status = "In Progress"
