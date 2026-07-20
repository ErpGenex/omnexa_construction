# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.subcontract_retention_release.subcontract_retention_release import (
	compute_retention_release,
)


class TestSubcontractRetention(FrappeTestCase):
	def test_net_release_percent(self):
		self.assertEqual(compute_retention_release(10000, 50), 5000)
		self.assertEqual(compute_retention_release(25000, 100), 25000)
