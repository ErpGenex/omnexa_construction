# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.regional_compliance.multi_entity import get_multi_entity_portfolio


class TestMultiEntityPortfolio(FrappeTestCase):
	def test_multi_entity(self):
		company = frappe.defaults.get_defaults().company
		out = get_multi_entity_portfolio(json.dumps([company]))
		self.assertGreaterEqual(out["contract_count"], 0)
		self.assertTrue(out.get("entities"))
