# Copyright (c) 2026, Omnexa and contributors

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.wizard.template_packs import (
	BOQ_TEMPLATES,
	BUILDING_TYPE_META,
	TEMPLATE_PACKS,
)


class TestAllBoqTemplates(FrappeTestCase):
	MIN_LINES = 18
	MIN_LEAF_LINES = 8
	MIN_PHASES = 4

	def test_all_building_types_have_template(self):
		for code in BUILDING_TYPE_META:
			meta = BUILDING_TYPE_META[code]
			self.assertTrue(meta.get("template_code"), f"Missing template_code for {code}")
			self.assertIn(meta["template_code"], TEMPLATE_PACKS, f"Pack missing for {code}")

	def test_template_catalog_size(self):
		self.assertEqual(len(TEMPLATE_PACKS), 50)
		self.assertEqual(len(BOQ_TEMPLATES), 50)
		self.assertEqual(len(BUILDING_TYPE_META), 50)

	def test_each_template_has_full_boq_structure(self):
		for code, pack in TEMPLATE_PACKS.items():
			lines = pack.get("lines") or []
			leaf = [r for r in lines if not r.get("is_group")]
			phases = pack.get("phases") or []
			self.assertGreaterEqual(len(lines), self.MIN_LINES, f"{code}: too few lines ({len(lines)})")
			self.assertGreaterEqual(len(leaf), self.MIN_LEAF_LINES, f"{code}: too few leaf lines")
			self.assertGreaterEqual(len(phases), self.MIN_PHASES, f"{code}: phases missing")
			self.assertTrue(pack.get("duration_months"), f"{code}: duration missing")
			prefixes = {str(r.get("cost_code", "")).split(".")[0] for r in lines if r.get("cost_code")}
			self.assertIn("00", prefixes, f"{code}: missing section 00 Preliminaries")

	def test_no_duplicate_cost_codes_in_templates(self):
		for code, pack in TEMPLATE_PACKS.items():
			codes = [r["cost_code"] for r in pack.get("lines") or []]
			self.assertEqual(len(codes), len(set(codes)), f"{code}: duplicate cost codes")

	def test_lump_sum_lines_do_not_use_area_drivers(self):
		for code, pack in TEMPLATE_PACKS.items():
			for row in pack.get("lines") or []:
				uom = (row.get("unit_of_measure") or "").strip().lower()
				driver = row.get("quantity_driver") or "FIXED"
				if uom == "ls" and driver in ("GFA", "PLOT", "FLOORS", "UNITS"):
					self.fail(f"{code} {row.get('cost_code')}: ls lines must use FIXED or FORMULA, not {driver}")
