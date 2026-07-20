# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Import Primavera P6 projects from XER into Project Contract + Schedule Baseline."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, today

from omnexa_construction.primavera_xer_parser import (
	extract_xer_projects,
	extract_xer_tasks,
	load_xer_content,
	parse_xer_sections,
	project_schedule_bounds,
)


def parse_xer_file(content: str) -> dict[str, list[dict]]:
	return parse_xer_sections(content)


@frappe.whitelist()
def preview_primavera_xer_import(file_url: str) -> dict:
	sections = parse_xer_file(load_xer_content(file_url))
	projects = extract_xer_projects(sections)
	if not projects:
		# Single-project export: derive one project from tasks
		tasks = extract_xer_tasks(sections)
		if not tasks:
			frappe.throw(_("No PROJECT or TASK data found in XER file."), title=_("Primavera Import"))
		start, end = project_schedule_bounds(tasks)
		projects = [
			{
				"proj_id": "XER-IMPORT",
				"name": _("Imported Primavera Schedule"),
				"description": "",
				"start_date": start,
				"end_date": end,
				"contract_value": 0
	}
		]

	preview = []
	for project in projects:
		proj_id = project["proj_id"]
		tasks = extract_xer_tasks(sections, None if proj_id == "XER-IMPORT" else proj_id)
		already = frappe.db.exists("Project Contract", {"p6_project_id": proj_id
	}) if proj_id != "XER-IMPORT" else None
		preview.append(
			{
				**project,
				"start_date": str(project["start_date"]) if project.get("start_date") else None,
				"end_date": str(project["end_date"]) if project.get("end_date") else None,
				"task_count": len(tasks),
				"already_imported": already
	}
		)

	return {
		"projects": preview,
		"total_projects": len(preview),
		"total_tasks": sum(p["task_count"] for p in preview)
	}


@frappe.whitelist()
def import_primavera_xer_projects(
	file_url: str,
	company: str,
	branch: str,
	client: str,
	project_ids: str | None = None,
	create_wbs_tasks: int = 0,
	submit_baseline: int = 1,
	contract_type: str = "Lump Sum",
	contract_status: str = "Active",
	skip_existing: int = 1,
) -> dict:
	if not all([file_url, company, branch, client]):
		frappe.throw(_("Company, Branch, Client, and XER file are required."), title=_("Primavera Import"))

	sections = parse_xer_file(load_xer_content(file_url))
	projects = extract_xer_projects(sections)
	if not projects:
		tasks = extract_xer_tasks(sections)
		if not tasks:
			frappe.throw(_("No importable data in XER file."), title=_("Primavera Import"))
		start, end = project_schedule_bounds(tasks)
		projects = [
			{
				"proj_id": "XER-IMPORT",
				"name": _("Imported Primavera Schedule"),
				"description": "",
				"start_date": start,
				"end_date": end,
				"contract_value": 0
	}
		]

	selected_ids: set[str] | None = None
	if project_ids:
		selected_ids = set(json.loads(project_ids))

	frappe.flags.in_primavera_xer_import = True
	results = []
	try:
		for project in projects:
			proj_id = project["proj_id"]
			if selected_ids is not None and proj_id not in selected_ids:
				continue

			if skip_existing and proj_id != "XER-IMPORT":
				existing = frappe.db.get_value("Project Contract", {"p6_project_id": proj_id
	}, "name")
				if existing:
					results.append(
						{
							"proj_id": proj_id,
							"status": "skipped",
							"project_contract": existing,
							"message": _("Already imported")
	}
					)
					continue

			try:
				result = _import_single_project(
					project=project,
					sections=sections,
					company=company,
					branch=branch,
					client=client,
					create_wbs_tasks=bool(int(create_wbs_tasks)),
					submit_baseline=bool(int(submit_baseline)),
					contract_type=contract_type,
					contract_status=contract_status,
				)
				results.append(result)
				frappe.db.commit()
			except Exception as exc:
				frappe.db.rollback()
				frappe.log_error(title=_("Primavera XER import failed"), message=frappe.get_traceback())
				results.append(
					{
						"proj_id": proj_id,
						"status": "failed",
						"message": str(exc)
	}
				)
	finally:
		frappe.flags.in_primavera_xer_import = False

	imported = sum(1 for r in results if r.get("status") == "success")
	return {
		"imported": imported,
		"results": results
	}


def _import_single_project(
	project: dict,
	sections: dict,
	company: str,
	branch: str,
	client: str,
	create_wbs_tasks: bool,
	submit_baseline: bool,
	contract_type: str,
	contract_status: str,
) -> dict:
	proj_id = project["proj_id"]
	tasks = extract_xer_tasks(sections, None if proj_id == "XER-IMPORT" else proj_id)
	start, end = project_schedule_bounds(tasks, project.get("start_date"), project.get("end_date"))

	contract = frappe.get_doc(
		{
			"doctype": "Project Contract",
			"contract_title": project["name"],
			"contract_type": contract_type or "Lump Sum",
			"client": client,
			"company": company,
			"branch": branch,
			"status": contract_status or "Active",
			"contract_value": project.get("contract_value") or 0,
			"planned_start": start,
			"planned_completion": end,
			"site_location": (project.get("description") or "")[:140] or None
	}
	)
	if frappe.get_meta("Project Contract").has_field("p6_project_id") and proj_id != "XER-IMPORT":
		contract.p6_project_id = proj_id
		if frappe.get_meta("Project Contract").has_field("p6_sync_status"):
			contract.p6_sync_status = "Synced"
		if frappe.get_meta("Project Contract").has_field("p6_last_sync"):
			contract.p6_last_sync = now_datetime()
	contract.insert(ignore_permissions=True)

	baseline = frappe.get_doc(
		{
			"doctype": "Construction Schedule Baseline",
			"project_contract": contract.name,
			"baseline_date": today(),
			"baseline_name": _("Primavera Import — {0}").format(project["name"])[:140],
			"planned_start": start,
			"planned_completion": end,
			"is_active": 1,
			"company": company,
			"branch": branch,
			"notes": _("Imported from Primavera XER on {0}").format(today())
	}
	)
	for task in tasks:
		row = {
			"task_name": task["task_name"],
			"start_date": task["start_date"],
			"end_date": task["end_date"],
			"duration_days": task["duration_days"],
			"is_milestone": task.get("is_milestone") or 0,
			"cost_code": task.get("cost_code")
	}
		meta = frappe.get_meta("Construction Schedule Baseline Task")
		if meta.has_field("predecessor_task") and task.get("predecessor_task"):
			row["predecessor_task"] = task["predecessor_task"]
		baseline.append("tasks", row)

	baseline.insert(ignore_permissions=True)
	if submit_baseline:
		baseline.submit()

	wbs_count = 0
	if create_wbs_tasks and tasks:
		wbs_count = _create_pm_wbs_tasks(contract.name, company, branch, tasks)

	return {
		"proj_id": proj_id,
		"status": "success",
		"project_contract": contract.name,
		"baseline": baseline.name,
		"tasks_imported": len(tasks),
		"wbs_tasks_created": wbs_count
	}


def _create_pm_wbs_tasks(project_contract: str, company: str, branch: str, tasks: list[dict]) -> int:
	meta = frappe.get_meta("PM WBS Task")
	count = 0
	for idx, task in enumerate(tasks, start=1):
		doc = {
			"doctype": "PM WBS Task",
			"project": project_contract,
			"task_name": task["task_name"],
			"planned_start": task["start_date"],
			"planned_end": task["end_date"],
			"sequence_no": idx,
			"status": "Planned",
			"company": company,
			"branch": branch
	}
		if meta.has_field("p6_activity_id") and task.get("task_id"):
			doc["p6_activity_id"] = task["task_id"]
		if meta.has_field("p6_sync_status"):
			doc["p6_sync_status"] = "Synced"
		frappe.get_doc(doc).insert(ignore_permissions=True)
		count += 1
	return count
