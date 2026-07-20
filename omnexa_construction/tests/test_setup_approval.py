# Copyright (c) 2026, Omnexa and contributors

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.setup_approval import is_setup_locked
from omnexa_construction.wizard.setup_contract_terms import suggest_contract_terms


class TestSetupApproval(FrappeTestCase):
	def test_suggest_contract_terms(self):
		setup = frappe.get_doc(
			{
				"doctype": "Construction Project Setup",
				"company": "_Test Company",
				"branch": "_Test Branch",
				"contract_title": "Test Tower",
				"contract_type": "Turnkey (EPC)",
				"contract_currency": "EGP",
				"building_type": "office_tower",
				"status": "Draft",
				"approval_status": "Open"
	}
		)
		count = suggest_contract_terms(setup)
		self.assertGreaterEqual(count, 6)
		self.assertFalse(is_setup_locked(setup))

		setup.approval_status = "Approved"
		self.assertTrue(is_setup_locked(setup))
