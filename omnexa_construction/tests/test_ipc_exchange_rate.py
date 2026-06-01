# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.ipc_revenue import _ipc_conversion_rate


class TestIpcExchangeRate(FrappeTestCase):
	def test_same_currency_returns_one(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		currency = frappe.db.get_value("Company", company, "default_currency")
		ipc = type(
			"IPC",
			(),
			{
				"company": company,
				"ipc_date": None,
				"meta": type("M", (), {"has_field": lambda _s, f: f == "exchange_rate"})(),
				"exchange_rate": 0,
			},
		)()
		self.assertEqual(_ipc_conversion_rate(ipc, currency), 1.0)

	def test_explicit_exchange_rate_used(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		currency = "USD"
		ipc = type(
			"IPC",
			(),
			{
				"company": company,
				"ipc_date": None,
				"meta": type("M", (), {"has_field": lambda _s, f: f == "exchange_rate"})(),
				"exchange_rate": 48.5,
			},
		)()
		self.assertEqual(_ipc_conversion_rate(ipc, currency), 48.5)
