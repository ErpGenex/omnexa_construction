# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.construction_integrations import dispatch_construction_event


class TestConstructionIntegrations(FrappeTestCase):
	def test_dispatch_noop_without_settings(self):
		doc = type("Doc", (), {"doctype": "Construction RFI", "name": "RFI-TEST-1", "project_contract": None, "company": "Test", "status": "Open"
	})()
		dispatch_construction_event(doc, "rfi.submitted")
