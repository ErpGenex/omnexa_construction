# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.site_invoice_ocr import parse_site_invoice_text


class TestSiteInvoiceOCR(FrappeTestCase):
	def test_parse_lines(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		raw = "Concrete supply 100 50 5000\nSteel bars 20 200 4000"
		out = parse_site_invoice_text(raw, contract[0])
		self.assertGreaterEqual(len(out["parsed_lines"]), 2)
