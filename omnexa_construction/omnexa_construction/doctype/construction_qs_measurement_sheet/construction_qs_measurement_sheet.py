import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
import csv
from io import StringIO


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


def _csv_qty(value) -> float:
	return flt(str(value or "").replace(",", "").strip() or 0)


@frappe.whitelist()
def import_takeoff_csv(project_contract: str, csv_text: str) -> list[dict]:
	"""Parse QS takeoff CSV and return lines ready for sheet child table."""
	if not project_contract:
		frappe.throw(_("Project Contract is required."))
	if not csv_text or not csv_text.strip():
		return []

	boq_rows = frappe.db.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "docstatus": ["!=", 2]},
		fields=["name", "cost_code", "item_description", "unit_of_measure", "quantity"],
		limit_page_length=5000,
	)
	by_code = {}
	for r in boq_rows:
		if r.get("cost_code") and r.get("cost_code") not in by_code:
			by_code[r.get("cost_code")] = r

	reader = csv.DictReader(StringIO(csv_text.strip()))
	out = []
	for row in reader:
		cost_code = (row.get("cost_code") or row.get("code") or "").strip()
		measured_qty = _csv_qty(row.get("measured_qty") or row.get("qty") or row.get("quantity"))
		description = (row.get("description") or row.get("item_description") or "").strip()
		uom = (row.get("uom") or row.get("unit_of_measure") or "").strip()
		if not cost_code and not description:
			continue
		boq = by_code.get(cost_code)
		out.append(
			{
				"boq_item": boq.get("name") if boq else None,
				"cost_code": cost_code or (boq.get("cost_code") if boq else ""),
				"description": description or (boq.get("item_description") if boq else ""),
				"unit_of_measure": uom or (boq.get("unit_of_measure") if boq else ""),
				"previous_qty": flt(boq.get("quantity")) if boq else 0,
				"measured_qty": measured_qty,
				"revision_qty": measured_qty - (flt(boq.get("quantity")) if boq else 0),
			}
		)
	return out
