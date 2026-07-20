import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, now_datetime

from omnexa_construction.bid_analysis import refresh_bid_scenario_margins


class ConstructionBidEstimate(Document):
	def validate(self):
		self.estimated_contract_value = flt(self.estimated_contract_value)
		self.estimated_cost = flt(self.estimated_cost)
		refresh_bid_scenario_margins(self)
		if self.estimated_contract_value < self.estimated_cost:
			frappe.msgprint(
				_("Estimated cost exceeds estimated contract value. Confirm pricing assumptions."),
				indicator="orange",
				alert=True,
			)


@frappe.whitelist()
def create_setup_from_bid_estimate(bid_estimate: str) -> dict:
	"""Create Construction Project Setup from an awarded bid estimate."""
	if not bid_estimate:
		frappe.throw(_("Bid Estimate is required."), title=_("Bid Estimate"))

	bid = frappe.get_doc("Construction Bid Estimate", bid_estimate)
	if bid.status not in ("Awarded", "Negotiated"):
		frappe.throw(_("Only Awarded/Negotiated bid estimates can be converted to setup."), title=_("Bid Estimate"))

	if bid.linked_project_setup and frappe.db.exists("Construction Project Setup", bid.linked_project_setup):
		return {"setup_name": bid.linked_project_setup, "already_linked": True
	}

	currency = frappe.db.get_value("Company", bid.company, "default_currency") or "EGP"
	planned_start = bid.expected_award_date or now_datetime().date()
	building_type = (bid.building_type or "").strip()
	if building_type:
		options_raw = (
			frappe.db.get_value(
				"DocField",
				{"parent": "Construction Project Setup", "fieldname": "building_type"
	},
				"options",
			)
			or ""
		)
		allowed = {opt.strip() for opt in options_raw.split("\n") if opt.strip()}
		if building_type not in allowed:
			building_type = ""

	setup = frappe.get_doc(
		{
			"doctype": "Construction Project Setup",
			"company": bid.company,
			"branch": bid.branch,
			"client": bid.customer,
			"contract_title": bid.estimate_title,
			"contract_currency": currency,
			"project_segment": bid.project_segment or "Buildings",
			"planned_start": planned_start,
			"planned_completion": add_days(planned_start, 180),
			"status": "Draft",
			"wizard_step": 1
	}
	)
	if building_type:
		setup.building_type = building_type
	setup.flags.wizard_save = True
	setup.insert(ignore_permissions=True)

	frappe.db.set_value(
		"Construction Bid Estimate",
		bid.name,
		{
			"linked_project_setup": setup.name,
			"status": "Awarded"
	},
		update_modified=True,
	)

	return {"setup_name": setup.name, "already_linked": False
	}
