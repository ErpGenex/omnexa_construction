# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_construction.primavera_project_import import import_primavera_xer_projects, preview_primavera_xer_import
from omnexa_construction.primavera_xer_parser import (
	extract_xer_projects,
	extract_xer_tasks,
	parse_xer_sections,
)
from omnexa_construction.schedule_xer_import import parse_xer_tasks

SAMPLE_XER = """ERMHDR\t18.8\t2024-01-01\tPROJECT\tadmin\t\t\t\t\t
%T\tPROJECT
%F\tproj_id\tproj_short_name\tplan_start_date\tplan_end_date\torig_cost
%R\t1001\tTower A\t2026-01-01 00:00\t2026-12-31 00:00\t2500000
%T\tTASK
%F\tproj_id\ttask_id\ttask_name\ttarget_start_date\ttarget_end_date\ttarget_drtn_hr_cnt\ttask_type
%R\t1001\t2001\tExcavation\t2026-01-01 00:00\t2026-01-31 00:00\t160\tTT_Task
%R\t1001\t2002\tStructure\t2026-02-01 00:00\t2026-06-30 00:00\t800\tTT_Task
%T\tTASKPRED
%F\ttask_id\tpred_task_id
%R\t2002\t2001
"""


class TestPrimaveraXerImport(FrappeTestCase):
	def test_parse_xer_sections(self):
		sections = parse_xer_sections(SAMPLE_XER)
		self.assertIn("PROJECT", sections)
		self.assertIn("TASK", sections)
		self.assertEqual(len(sections["PROJECT"]), 1)
		self.assertEqual(len(sections["TASK"]), 2)

	def test_extract_projects_and_tasks(self):
		sections = parse_xer_sections(SAMPLE_XER)
		projects = extract_xer_projects(sections)
		self.assertEqual(projects[0]["proj_id"], "1001")
		self.assertEqual(projects[0]["name"], "Tower A")
		tasks = extract_xer_tasks(sections, "1001")
		self.assertEqual(len(tasks), 2)
		self.assertEqual(tasks[1]["predecessor_task"], "Excavation")

	def test_parse_xer_tasks_compat(self):
		tasks = parse_xer_tasks(SAMPLE_XER)
		self.assertEqual(len(tasks), 2)

	def test_import_creates_project_contract(self):
		company = frappe.db.get_value("Company", {}, "name")
		if not company:
			self.skipTest("No company")
		branch = frappe.db.get_value("Branch", {"company": company}, "name")
		if not branch:
			self.skipTest("No branch")
		client = frappe.db.get_value("Customer", {}, "name")
		if not client:
			self.skipTest("No customer")

		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": "test_import.xer",
				"content": SAMPLE_XER,
				"is_private": 1,
			}
		).insert(ignore_permissions=True)

		preview = preview_primavera_xer_import(file_doc.file_url)
		self.assertEqual(preview["total_projects"], 1)
		self.assertEqual(preview["projects"][0]["task_count"], 2)

		result = import_primavera_xer_projects(
			file_url=file_doc.file_url,
			company=company,
			branch=branch,
			client=client,
			project_ids='["1001"]',
			create_wbs_tasks=1,
			submit_baseline=0,
			skip_existing=0,
		)
		self.assertEqual(result["imported"], 1, msg=str(result.get("results")))
		contract_name = result["results"][0]["project_contract"]
		self.assertTrue(frappe.db.exists("Project Contract", contract_name))
		self.assertEqual(frappe.db.get_value("Project Contract", contract_name, "p6_project_id"), "1001")
		baseline = frappe.db.get_value(
			"Construction Schedule Baseline",
			{"project_contract": contract_name},
			"name",
		)
		self.assertTrue(baseline)
		task_count = frappe.db.count("Construction Schedule Baseline Task", {"parent": baseline})
		self.assertEqual(task_count, 2)
		wbs_count = frappe.db.count("PM WBS Task", {"project": contract_name})
		self.assertEqual(wbs_count, 2)
