import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt


class ConstructionProjectRisk(Document):
	def validate(self):
		self.probability = max(1, min(5, cint(self.probability or 1)))
		self.impact = max(1, min(5, cint(self.impact or 1)))
		self.risk_score = flt(self.probability) * flt(self.impact)
		if self.linked_eot:
			project = frappe.db.get_value("Construction Extension of Time", self.linked_eot, "project_contract")
			if project and project != self.project_contract:
				frappe.throw(_("Related EOT must belong to the same Project Contract."), title=_("Risk Register"))
		if self.linked_claim:
			project = frappe.db.get_value("Construction Claim", self.linked_claim, "project_contract")
			if project and project != self.project_contract:
				frappe.throw(_("Related Claim must belong to the same Project Contract."), title=_("Risk Register"))
