# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase

from omnexa_construction.omnexa_construction.doctype.construction_cbs_element.construction_cbs_element import (
	suggest_cbs_for_cost_code,
)
from omnexa_construction.utils.cbs_boq import cbs_boq_summary


class TestCbsBoq(FrappeTestCase):
	@patch(
		"omnexa_construction.omnexa_construction.doctype.construction_cbs_element.construction_cbs_element.frappe.get_all",
		return_value=[{"name": "CBS-03", "cost_code_prefix": "03"
	}],
	)
	def test_suggest_cbs_from_prefix(self, _rows):
		self.assertEqual(suggest_cbs_for_cost_code("03.10.20"), "CBS-03")

	@patch(
		"omnexa_construction.utils.cbs_boq.frappe.get_all",
		return_value=[
			{"cbs_element": "CBS-03", "planned_cost": 100, "actual_cost": 80, "cost_code": "03.10"
	},
			{"cbs_element": None, "planned_cost": 50, "actual_cost": 40, "cost_code": "03.20"
	},
		],
	)
	@patch(
		"omnexa_construction.utils.cbs_boq.suggest_cbs_for_cost_code",
		return_value="CBS-03",
	)
	def test_cbs_summary_aggregates(self, _suggest, _boq):
		rows = cbs_boq_summary("CTR-1")
		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["planned_cost"], 150)
