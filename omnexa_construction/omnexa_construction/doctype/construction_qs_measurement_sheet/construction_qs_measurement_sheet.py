import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ConstructionQSMeasurementSheet(Document):
	def validate(self):
		for row in self.lines or []:
			if row.boq_item:
				boq = frappe.db.get_value(
					"BOQ Item",
					row.boq_item,
					["cost_code", "item_description", "unit_of_measure", "quantity", "project_contract"],
					as_dict=True,
				)
				if boq:
					if boq.project_contract != self.project_contract:
						frappe.throw(_("BOQ item {0} does not belong to this contract.").format(row.boq_item))
					row.cost_code = row.cost_code or boq.cost_code
					row.description = row.description or boq.item_description
					row.unit_of_measure = row.unit_of_measure or boq.unit_of_measure
					row.previous_qty = flt(boq.quantity)
			row.revision_qty = flt(row.measured_qty) - flt(row.previous_qty)

	def on_submit(self):
		if not self.apply_to_boq:
			return
		for row in self.lines or []:
			if not row.boq_item:
				continue
			frappe.db.set_value(
				"BOQ Item",
				row.boq_item,
				"quantity",
				flt(row.measured_qty),
				update_modified=True,
			)
			uc = flt(frappe.db.get_value("BOQ Item", row.boq_item, "unit_cost"))
			frappe.db.set_value(
				"BOQ Item",
				row.boq_item,
				"planned_cost",
				flt(row.measured_qty) * uc,
				update_modified=True,
			)
