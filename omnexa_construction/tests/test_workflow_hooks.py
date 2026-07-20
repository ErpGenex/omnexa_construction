# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.workflow_hooks import validate_construction_workflow_binding


class TestWorkflowHooks(FrappeTestCase):
	@patch("omnexa_construction.workflow_hooks.frappe.db.get_single_value", return_value=0)
	@patch("omnexa_construction.workflow_hooks.frappe.db.exists", return_value=True)
	def test_skips_when_strict_binding_disabled(self, _exists, _single):
		doc = type("Doc", (), {"doctype": "IPC Certificate", "project_contract": "CNT-1", "flags": type("F", (), {})()})()
		validate_construction_workflow_binding(doc)
		self.assertFalse(hasattr(doc, "project") and doc.project == "CNT-1")
