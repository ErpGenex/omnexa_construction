# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.procurement_rfq import _winning_quote


class TestRfqAwardPo(FrappeTestCase):
	def test_winning_quote_matches_supplier(self):
		rfq = type(
			"RFQ",
			(),
			{
				"supplier_quotes": [
					type("Q", (), {"supplier": "SUP-A", "quoted_amount": 1000
	})(),
					type("Q", (), {"supplier": "SUP-B", "quoted_amount": 900
	})(),
				]
			},
		)()
		quote = _winning_quote(rfq, "SUP-B")
		self.assertIsNotNone(quote)
		self.assertEqual(quote.quoted_amount, 900)

	def test_winning_quote_missing_supplier(self):
		rfq = type("RFQ", (), {"supplier_quotes": []
	})()
		self.assertIsNone(_winning_quote(rfq, "SUP-X"))

	def test_proportional_rate_from_quote(self):
		rfq = type(
			"RFQ",
			(),
			{
				"estimated_total": 1000,
				"items": [type("I", (), {"amount": 400, "quantity": 4, "estimated_rate": 100
	})()],
				"supplier_quotes": [type("Q", (), {"supplier": "SUP-A", "quoted_amount": 800})()]
	},
		)()
		quote = _winning_quote(rfq, "SUP-A")
		share = rfq.items[0].amount / rfq.estimated_total
		rate = (quote.quoted_amount * share / rfq.items[0].quantity)
		self.assertEqual(rate, 80.0)
