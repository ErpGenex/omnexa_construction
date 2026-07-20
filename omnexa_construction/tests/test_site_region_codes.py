# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.site_region_codes import get_site_region_options
from omnexa_construction.wizard.wizard_api import list_site_region_code_options


class TestSiteRegionCodes(FrappeTestCase):
	def test_includes_iso_countries(self):
		rows = get_site_region_options()
		codes = {r["region_code"] for r in rows}
		self.assertIn("EG", codes)
		self.assertIn("US", codes)
		self.assertIn("SA", codes)
		self.assertGreaterEqual(len(codes), 200)

	def test_search_filters(self):
		rows = get_site_region_options(search="egypt")
		self.assertTrue(any(r["region_code"] == "EG" for r in rows))

	def test_whitelist_api(self):
		result = list_site_region_code_options()
		self.assertIsInstance(result, list)
		self.assertGreater(len(result), 100)
