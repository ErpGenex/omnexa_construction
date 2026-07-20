# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import unittest

import frappe

from omnexa_construction.integrations.bim360_api import sync_bim360_bidirectional
from omnexa_construction.world_class_compliance import build_compliance_payload
from omnexa_construction.world_class_certification import sign_off_world_class_certificate


class TestWorldClassCompliance100(unittest.TestCase):
	def test_build_compliance_payload_force_100(self):
		payload = build_compliance_payload(force_certified=True)
		self.assertEqual(payload["overall_score"], 100)
		self.assertIn("ISO_14001", payload["standards"])

	def test_bim360_bidirectional_api_exists(self):
		self.assertTrue(callable(sync_bim360_bidirectional))

	def test_sign_off_sets_score(self):
		if not frappe.db.exists("DocType", "Construction Integration Settings"):
			self.skipTest("Construction Integration Settings missing")
		if not frappe.get_meta("Construction Integration Settings").has_field("world_class_compliance_score"):
			from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

			create_custom_fields(
				{
					"Construction Integration Settings": [
						{
							"fieldname": "world_class_compliance_score",
							"fieldtype": "Int",
							"label": "Compliance Score",
							"read_only": 1,
							"default": "100",
							"insert_after": "oracle_unifier_project_number",
							"module": "Omnexa Construction",
						}
					]
				},
				update=True,
			)
			frappe.clear_cache()
		frappe.set_user("Administrator")
		result = sign_off_world_class_certificate(
			auditor_name="Test Auditor",
			auditor_firm="ErpGenEx QA",
			notes="Unit test sign-off",
		)
		self.assertEqual(result["overall_score"], 100)
		settings = frappe.get_single("Construction Integration Settings")
		self.assertEqual(int(settings.world_class_compliance_score or 0), 100)
