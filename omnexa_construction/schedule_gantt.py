from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate


def _resolve_schedule_baseline(project_contract: str) -> dict | None:
	"""Pick baseline for Gantt: submitted active → submitted → active draft → draft with tasks."""
	active_submitted = frappe.db.get_value(
		"Construction Schedule Baseline",
		{"project_contract": project_contract, "is_active": 1, "docstatus": 1},
		["name", "planned_start", "planned_completion", "baseline_name", "docstatus"],
		as_dict=True,
	)
	if active_submitted:
		return active_submitted

	submitted = frappe.get_all(
		"Construction Schedule Baseline",
		filters={"project_contract": project_contract, "docstatus": 1},
		fields=["name", "planned_start", "planned_completion", "baseline_name", "docstatus"],
		order_by="modified desc",
		limit_page_length=1,
	)
	if submitted:
		return submitted[0]

	active_draft = frappe.db.get_value(
		"Construction Schedule Baseline",
		{"project_contract": project_contract, "is_active": 1, "docstatus": 0},
		["name", "planned_start", "planned_completion", "baseline_name", "docstatus"],
		as_dict=True,
	)
	if active_draft:
		return active_draft

	candidates = frappe.get_all(
		"Construction Schedule Baseline",
		filters={"project_contract": project_contract, "docstatus": ["<", 2]},
		fields=["name", "planned_start", "planned_completion", "baseline_name", "docstatus"],
		order_by="modified desc",
		limit_page_length=20,
	)
	for row in candidates:
		if frappe.db.count("Construction Schedule Baseline Task", {"parent": row.name}):
			return row
	return candidates[0] if candidates else None


@frappe.whitelist()
def get_schedule_gantt_data(project_contract: str) -> dict:
	"""Gantt payload from schedule baseline tasks + BOQ progress."""
	if not project_contract:
		frappe.throw(_("Project Contract is required."), title=_("Schedule Gantt"))

	baseline = _resolve_schedule_baseline(project_contract)

	tasks = []
	critical_names: set[str] = set()
	baseline_name = (baseline or {}).get("name")
	if baseline_name:
		fields = [
			"task_name",
			"start_date",
			"end_date",
			"duration_days",
			"boq_item",
			"cost_code",
			"progress_percent",
			"is_milestone",
		]
		meta = frappe.get_meta("Construction Schedule Baseline Task")
		if meta.has_field("predecessor_task"):
			fields.append("predecessor_task")
		rows = frappe.get_all(
			"Construction Schedule Baseline Task",
			filters={"parent": baseline_name},
			fields=fields,
			order_by="start_date asc",
			limit_page_length=500,
		)
		task_rows = []
		for row in rows:
			progress = flt(row.get("progress_percent"))
			boq_item = row.get("boq_item")
			if boq_item:
				progress = flt(frappe.db.get_value("BOQ Item", boq_item, "completion_percent"))
			task_rows.append(
				{
					"task_name": row.get("task_name"),
					"start_date": row.get("start_date"),
					"end_date": row.get("end_date"),
					"duration_days": row.get("duration_days"),
					"predecessor_task": row.get("predecessor_task"),
					"progress_percent": progress,
					"boq_item": boq_item,
					"cost_code": row.get("cost_code"),
					"is_milestone": row.get("is_milestone"),
				}
			)

		from omnexa_construction.schedule_critical_path import compute_critical_path

		critical_names = set(compute_critical_path(task_rows))
		for row in task_rows:
			progress = flt(row.get("progress_percent"))
			tasks.append(
				{
					"id": row.get("task_name"),
					"name": row.get("task_name"),
					"start": str(row.get("start_date")),
					"end": str(row.get("end_date")),
					"progress": progress,
					"boq_item": row.get("boq_item"),
					"cost_code": row.get("cost_code"),
					"is_milestone": row.get("is_milestone"),
					"dependencies": row.get("predecessor_task") or "",
					"is_critical": row.get("task_name") in critical_names,
					"custom_class": row.get("task_name") in critical_names and "bar-critical" or "",
				}
			)

	return {
		"project_contract": project_contract,
		"baseline": baseline,
		"baseline_is_draft": bool(baseline and int(baseline.get("docstatus") or 0) == 0),
		"tasks": tasks,
		"critical_path": list(critical_names),
	}


@frappe.whitelist()
def load_baseline_tasks_from_boq(baseline_name: str) -> dict:
	"""Populate baseline task child rows from leaf BOQ lines."""
	baseline = frappe.get_doc("Construction Schedule Baseline", baseline_name)
	if not baseline.project_contract:
		frappe.throw(_("Project Contract is required on baseline."), title=_("Schedule"))

	start = getdate(baseline.planned_start)
	end = getdate(baseline.planned_completion)
	total_days = max(date_diff(end, start), 1)

	boq_lines = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": baseline.project_contract, "is_group": 0, "docstatus": ["!=", 2]},
		fields=["name", "item_description", "cost_code", "completion_percent"],
		order_by="cost_code asc",
		limit_page_length=200,
	)
	if not boq_lines:
		return {"added": 0}

	baseline.set("tasks", [])
	span = max(total_days // len(boq_lines), 1)
	for idx, line in enumerate(boq_lines):
		task_start = frappe.utils.add_days(start, idx * span)
		task_end = frappe.utils.add_days(task_start, span - 1)
		if task_end > end:
			task_end = end
		baseline.append(
			"tasks",
			{
				"task_name": (line.item_description or line.name)[:140],
				"start_date": task_start,
				"end_date": task_end,
				"duration_days": date_diff(task_end, task_start) + 1,
				"boq_item": line.name,
				"cost_code": line.cost_code,
				"progress_percent": flt(line.completion_percent),
			},
		)
	baseline.flags.ignore_validate = True
	baseline.save(ignore_permissions=True)
	return {"added": len(boq_lines)}
