# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.bid_analysis import compare_bids_in_package, run_sensitivity_analysis


class TestBidAnalysis(FrappeTestCase):
	@patch(
		"omnexa_construction.bid_analysis.frappe.get_all",
		return_value=[
			{
				"name": "BID-1",
				"estimate_title": "Alt A",
				"customer": "C1",
				"status": "Submitted",
				"estimated_contract_value": 1000000,
				"estimated_cost": 850000,
				"target_margin_percent": 15,
				"proposal_date": None,
			},
			{
				"name": "BID-2",
				"estimate_title": "Alt B",
				"customer": "C2",
				"status": "Submitted",
				"estimated_contract_value": 950000,
				"estimated_cost": 800000,
				"target_margin_percent": 15,
				"proposal_date": None,
			},
		],
	)
	def test_compare_marks_lowest_bid(self, _rows):
		out = compare_bids_in_package("PKG-01")
		self.assertEqual(len(out), 2)
		lowest = [r for r in out if r.get("is_lowest")][0]
		self.assertEqual(lowest["name"], "BID-2")

	@patch(
		"omnexa_construction.bid_analysis.frappe.get_doc",
		return_value=type(
			"Bid",
			(),
			{"estimated_contract_value": 1000, "estimated_cost": 800},
		)(),
	)
	def test_sensitivity_returns_matrix(self, _doc):
		rows = run_sensitivity_analysis("BID-1", cost_deltas=[0], price_deltas=[0, 5])
		self.assertEqual(len(rows), 2)
		self.assertIn("projected_margin_percent", rows[0])
