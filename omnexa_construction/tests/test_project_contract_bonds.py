# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.project_contract.project_contract import ProjectContract


class TestProjectContractBonds(FrappeTestCase):
	def test_bond_amount_from_percent(self):
		doc = frappe._dict(
			contract_value=1000000,
			revised_contract_value=1000000,
			contract_bonds=[frappe._dict(bond_type="Performance Bond", percent_of_contract=10, bond_amount=0)],
		)
		ProjectContract._normalize_contract_bonds(doc)
		self.assertEqual(doc.contract_bonds[0].bond_amount, 100000)
