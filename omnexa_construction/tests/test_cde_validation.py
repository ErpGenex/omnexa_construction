# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.cde_validation import _pattern_from_convention, validate_cde_document_number


class TestCdeValidation(FrappeTestCase):
	def test_strict_pattern_accepts_valid_code(self):
		doc = frappe._dict(naming_convention="STRICT", document_number="PRJ-CTR-DRW-0001-A")
		validate_cde_document_number(doc)

	def test_relaxed_pattern_accepts_dashes(self):
		doc = frappe._dict(naming_convention="RELAXED", document_number="prj_drawing_01")
		validate_cde_document_number(doc)

	def test_pattern_from_convention_defaults_strict(self):
		pattern = _pattern_from_convention("STRICT")
		self.assertTrue(pattern.match("ABC-XY-ZZZ-1234-B"))
