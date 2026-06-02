# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import Mock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate import (
	create_setup_from_bid_estimate,
)


class TestBidEstimate(FrappeTestCase):
	def test_bid_estimate_accepts_basic_payload(self):
		doc = frappe.get_doc(
			{
				"doctype": "Construction Bid Estimate",
				"estimate_title": "Tower A Bid",
				"customer": "_Test Customer",
				"estimated_contract_value": 1000000,
				"estimated_cost": 850000,
				"company": "_Test Company",
				"branch": "_Test Branch",
			}
		)
		doc.flags.wizard_save = True
		with patch("omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.msgprint"):
			doc.run_method("validate")
		self.assertEqual(doc.estimated_contract_value, 1000000)

	def test_bid_estimate_warns_when_cost_exceeds_value(self):
		doc = frappe.get_doc(
			{
				"doctype": "Construction Bid Estimate",
				"estimate_title": "Tower B Bid",
				"customer": "_Test Customer",
				"estimated_contract_value": 100,
				"estimated_cost": 120,
				"company": "_Test Company",
				"branch": "_Test Branch",
			}
		)
		doc.flags.wizard_save = True
		with patch(
			"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.msgprint"
		) as mock_msg:
			doc.run_method("validate")
		mock_msg.assert_called_once()

	def test_create_setup_from_awarded_bid(self):
		bid = frappe._dict(
			{
				"name": "BID-2026-00001",
				"status": "Awarded",
				"linked_project_setup": None,
				"company": "_Test Company",
				"branch": "_Test Branch",
				"customer": "_Test Customer",
				"estimate_title": "Tower C Bid",
				"project_segment": "Buildings",
				"building_type": "residential_building",
				"expected_award_date": "2026-06-02",
			}
		)
		setup = frappe._dict({"name": "CPS-00001"})
		setup.flags = frappe._dict()
		setup.insert = Mock()

		def _fake_get_doc(arg1, arg2=None):
			if arg1 == "Construction Bid Estimate":
				return bid
			if isinstance(arg1, dict) and arg1.get("doctype") == "Construction Project Setup":
				return setup
			raise AssertionError(f"Unexpected get_doc call: {arg1!r}")

		with (
			patch(
				"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.get_doc",
				side_effect=_fake_get_doc,
			),
			patch(
				"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.db.exists",
				return_value=False,
			),
			patch(
				"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.db.get_value",
				side_effect=["EGP", "residential_building\nhotel\nhospital"],
			),
			patch(
				"omnexa_construction.omnexa_construction.doctype.construction_bid_estimate.construction_bid_estimate.frappe.db.set_value"
			) as mock_set,
		):
			out = create_setup_from_bid_estimate("BID-2026-00001")
		self.assertEqual(out.get("setup_name"), "CPS-00001")
		mock_set.assert_called_once()
