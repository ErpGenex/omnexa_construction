# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.procurement_rfq import _winning_quote


class TestProcurementRfq(FrappeTestCase):
	def test_winning_quote_matches_supplier(self):
		rfq = type(
			"RFQ",
			(),
			{
				"supplier_quotes": [
					type("Q", (), {"supplier": "SUP-A", "quoted_amount": 1000})(),
					type("Q", (), {"supplier": "SUP-B", "quoted_amount": 900})(),
				]
			},
		)()
		quote = _winning_quote(rfq, "SUP-B")
		self.assertEqual(quote.quoted_amount, 900)

	def test_winning_quote_missing_returns_none(self):
		rfq = type("RFQ", (), {"supplier_quotes": []})()
		self.assertIsNone(_winning_quote(rfq, "NONE"))
