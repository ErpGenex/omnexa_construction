# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.fidic_assistant import draft_fidic_notice_suggestion, suggest_fidic_clause


class TestFIDICAssistant(FrappeTestCase):
	def test_suggest_clause_returns_list(self):
		import frappe

		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		rows = suggest_fidic_clause(contract[0], notice_type="Claim")
		self.assertIsInstance(rows, list)

	def test_draft_notice_suggestion(self):
		import frappe

		contract = frappe.get_all("Project Contract", limit=1, pluck="name")
		if not contract:
			self.skipTest("No contract")
		out = draft_fidic_notice_suggestion(contract[0], "Claim")
		self.assertIn("draft", out)
		self.assertIn("assistant_message", out)
