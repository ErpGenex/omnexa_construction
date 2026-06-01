# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests import IntegrationTestCase

from omnexa_construction.boq_commitment import committed_amount_for_boq


class TestBoqCommitment(IntegrationTestCase):
	def test_committed_amount_no_crash(self):
		self.assertEqual(committed_amount_for_boq("NONEXISTENT-BOQ"), 0.0)

	def test_boq_has_committed_field(self):
		meta = frappe.get_meta("BOQ Item")
		self.assertTrue(meta.has_field("committed_cost"))
