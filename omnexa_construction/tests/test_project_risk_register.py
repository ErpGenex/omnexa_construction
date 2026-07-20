# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

class TestProjectRiskRegister(FrappeTestCase):
	def test_risk_score_is_probability_times_impact(self):
		doc = frappe.get_doc(
			{
				"doctype": "Construction Project Risk",
				"project_contract": "CTR-1",
				"probability": 4,
				"impact": 3,
				"company": "_Test Company",
				"branch": "_Test Branch",
			}
		)
		with patch("omnexa_construction.omnexa_construction.doctype.construction_project_risk.construction_project_risk.frappe.db.get_value", return_value=None):
			doc.validate()
		self.assertEqual(doc.risk_score, 12.0)

	def test_probability_and_impact_clamped(self):
		doc = frappe.get_doc(
			{
				"doctype": "Construction Project Risk",
				"project_contract": "CTR-1",
				"probability": 99,
				"impact": 0,
				"company": "_Test Company",
				"branch": "_Test Branch",
			}
		)
		with patch("omnexa_construction.omnexa_construction.doctype.construction_project_risk.construction_project_risk.frappe.db.get_value", return_value=None):
			doc.validate()
		self.assertEqual(doc.probability, 5)
		self.assertEqual(doc.impact, 1)
