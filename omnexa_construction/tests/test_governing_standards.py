from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.governing_standards import (
	GOVERNING_CONTRACT_FORM_OPTIONS,
	normalize_governing_standard,
)


class TestGoverningStandards(FrappeTestCase):
	def test_short_red_book(self):
		out = normalize_governing_standard("FIDIC 2017 Red Book")
		self.assertEqual(out, GOVERNING_CONTRACT_FORM_OPTIONS[0])

	def test_turnkey_default_silver(self):
		out = normalize_governing_standard("", contract_type="Turnkey (EPC)")
		self.assertEqual(out, GOVERNING_CONTRACT_FORM_OPTIONS[2])

	def test_full_value_unchanged(self):
		val = GOVERNING_CONTRACT_FORM_OPTIONS[1]
		self.assertEqual(normalize_governing_standard(val), val)
