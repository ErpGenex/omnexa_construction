# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import time

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBOQ10kPerformance(FrappeTestCase):
	"""Assert BOQ list query stays under threshold for 10k-scale datasets."""

	THRESHOLD_SEC = 5.0

	def test_boq_count_and_list_performance(self):
		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No project contract")
		filters = {"project_contract": contract[0], "docstatus": ["<", 2]}
		start = time.perf_counter()
		count = frappe.db.count("BOQ Item", filters)
		meta = frappe.get_meta("BOQ Item")
		fields = ["name"]
		for f in ("description", "qty", "rate", "amount", "cost_code"):
			if meta.has_field(f):
				fields.append(f)
		rows = frappe.get_all(
			"BOQ Item",
			filters=filters,
			fields=fields,
			limit_page_length=10000,
		)
		elapsed = time.perf_counter() - start
		self.assertLess(
			elapsed,
			self.THRESHOLD_SEC,
			f"BOQ query took {elapsed:.2f}s (count={count}, rows={len(rows)})",
		)
