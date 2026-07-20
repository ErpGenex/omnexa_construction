from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt


def _margin_percent(contract_value: float, cost: float) -> float:
	if not contract_value:
		return 0.0
	return round(((flt(contract_value) - flt(cost)) / flt(contract_value)) * 100, 2)


def _adjusted_values(base_value: float, base_cost: float, cost_adj_pct: float, price_adj_pct: float) -> tuple[float, float]:
	value = flt(base_value) * (1 + flt(price_adj_pct) / 100)
	cost = flt(base_cost) * (1 + flt(cost_adj_pct) / 100)
	return value, cost


@frappe.whitelist()
def compare_bids_in_package(bid_package: str, company: str | None = None) -> list[dict]:
	"""Compare bid estimates sharing the same bid package code."""
	if not (bid_package or "").strip():
		frappe.throw(_("Bid Package is required."), title=_("Bid Comparison"))

	filters = {"bid_package": bid_package.strip(), "docstatus": ["<", 2]}
	if company:
		filters["company"] = company

	rows = frappe.get_all(
		"Construction Bid Estimate",
		filters=filters,
		fields=[
			"name",
			"estimate_title",
			"customer",
			"status",
			"estimated_contract_value",
			"estimated_cost",
			"target_margin_percent",
			"proposal_date",
		],
		order_by="estimated_contract_value asc",
		limit_page_length=100,
	)
	if not rows:
		return []

	lowest_value = min(flt(r.get("estimated_contract_value")) for r in rows)
	out = []
	for r in rows:
		margin = _margin_percent(r.get("estimated_contract_value"), r.get("estimated_cost"))
		out.append(
			{
				**r,
				"margin_percent": margin,
				"variance_to_lowest": flt(r.get("estimated_contract_value")) - lowest_value,
				"is_lowest": 1 if flt(r.get("estimated_contract_value")) == lowest_value else 0,
			}
		)
	return out


@frappe.whitelist()
def run_sensitivity_analysis(
	bid_estimate: str,
	cost_deltas: str | list | None = None,
	price_deltas: str | list | None = None,
) -> list[dict]:
	"""Return sensitivity matrix for cost/price delta percentages."""
	import json

	bid = frappe.get_doc("Construction Bid Estimate", bid_estimate)
	base_value = flt(bid.estimated_contract_value)
	base_cost = flt(bid.estimated_cost)
	base_margin = _margin_percent(base_value, base_cost)

	if isinstance(cost_deltas, str):
		cost_deltas = json.loads(cost_deltas) if cost_deltas else [-10, -5, 0, 5, 10]
	if isinstance(price_deltas, str):
		price_deltas = json.loads(price_deltas) if price_deltas else [-5, 0, 5]
	if not cost_deltas:
		cost_deltas = [-10, -5, 0, 5, 10]
	if not price_deltas:
		price_deltas = [-5, 0, 5]

	matrix = []
	for cost_adj in cost_deltas:
		for price_adj in price_deltas:
			value, cost = _adjusted_values(base_value, base_cost, cost_adj, price_adj)
			margin = _margin_percent(value, cost)
			matrix.append(
				{
					"scenario": f"C{cost_adj:+g}% / P{price_adj:+g}%",
					"cost_adjustment_percent": flt(cost_adj),
					"price_adjustment_percent": flt(price_adj),
					"projected_contract_value": round(value, 2),
					"projected_cost": round(cost, 2),
					"projected_margin_percent": margin,
					"margin_delta_vs_base": round(margin - base_margin, 2),
				}
			)
	return matrix


def refresh_bid_scenario_margins(doc) -> None:
	"""Populate child scenario projected margins on validate."""
	base_value = flt(doc.estimated_contract_value)
	base_cost = flt(doc.estimated_cost)
	for row in doc.get("scenarios") or []:
		value, cost = _adjusted_values(
			base_value,
			base_cost,
			row.cost_adjustment_percent,
			row.price_adjustment_percent,
		)
		row.projected_margin_percent = _margin_percent(value, cost)
