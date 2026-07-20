# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Primavera P6 XER file parser (tab-delimited sections)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate


def load_xer_content(file_url: str) -> str:
	if not file_url:
		frappe.throw(_("XER file is required."), title=_("Primavera Import"))
	content = frappe.get_doc("File", {"file_url": file_url
	}).get_content()
	if isinstance(content, bytes):
		content = content.decode("utf-8", errors="replace")
	if not content.strip():
		frappe.throw(_("XER file is empty."), title=_("Primavera Import"))
	return content


def parse_xer_file(content: str) -> dict[str, list[dict[str, str]]]:
	"""Alias for parse_xer_sections."""
	return parse_xer_sections(content)


def parse_xer_sections(content: str) -> dict[str, list[dict[str, str]]]:
	"""Return {section_name: [row_dict, ...]} from a Primavera XER export."""
	lines = content.replace("\r\n", "\n").split("\n")
	sections: dict[str, dict] = {}
	current: str | None = None
	fields: list[str] = []

	for line in lines:
		if not line.strip():
			continue
		parts = line.split("\t")
		tag = parts[0]
		if tag == "%T":
			current = parts[1].strip() if len(parts) > 1 else None
			fields = []
			if current and current not in sections:
				sections[current] = {"fields": [], "rows": []
	}
			continue
		if not current:
			continue
		if tag == "%T":
			break
		if tag == "%F":
			fields = [p.strip() for p in parts[1:]]
			sections[current]["fields"] = fields
			continue
		if tag == "%R" and fields:
			vals = parts[1:]
			sections[current]["rows"].append(dict(zip(fields, vals, strict=False)))

	return {name: data["rows"] for name, data in sections.items() if data.get("rows")}


def parse_xer_date(value: str | None):
	if not value:
		return None
	value = value.strip()
	if len(value) >= 10:
		try:
			return getdate(value[:10])
		except Exception:
			return None
	return None


def date_diff_safe(end, start) -> int:
	from frappe.utils import date_diff

	try:
		return date_diff(end, start)
	except Exception:
		return 0


def extract_xer_projects(sections: dict[str, list[dict]]) -> list[dict]:
	rows = sections.get("PROJECT") or []
	projects: list[dict] = []
	for row in rows:
		proj_id = (row.get("proj_id") or row.get("project_id") or "").strip()
		if not proj_id:
			continue
		name = (
			row.get("proj_short_name")
			or row.get("proj_name")
			or row.get("project_short_name")
			or proj_id
		).strip()
		start = parse_xer_date(
			row.get("plan_start_date")
			or row.get("scd_start_date")
			or row.get("act_start_date")
			or row.get("target_start_date")
		)
		end = parse_xer_date(
			row.get("plan_end_date")
			or row.get("scd_end_date")
			or row.get("act_end_date")
			or row.get("target_end_date")
		)
		cost = flt(row.get("orig_cost") or row.get("total_cost") or row.get("sum_base_cost") or 0)
		projects.append(
			{
				"proj_id": proj_id,
				"name": name[:140],
				"description": (row.get("proj_desc") or row.get("project_desc") or "")[:500],
				"start_date": start,
				"end_date": end,
				"contract_value": cost
	}
		)
	return projects


def extract_xer_tasks(sections: dict[str, list[dict]], proj_id: str | None = None) -> list[dict]:
	rows = sections.get("TASK") or []
	taskpred = sections.get("TASKPRED") or []
	task_id_to_name = {
		(row.get("task_id") or "").strip(): (
			row.get("task_name") or row.get("task_code") or row.get("wbs_name") or ""
		).strip()
		for row in rows
	}
	pred_map: dict[str, list[str]] = {}
	for row in taskpred:
		task_id = (row.get("task_id") or "").strip()
		pred_id = (row.get("pred_task_id") or row.get("pred_task") or "").strip()
		if task_id and pred_id:
			pred_map.setdefault(task_id, []).append(pred_id)

	tasks: list[dict] = []
	for row in rows:
		row_proj = (row.get("proj_id") or row.get("project_id") or "").strip()
		if proj_id and row_proj and row_proj != proj_id:
			continue
		task_id = (row.get("task_id") or "").strip()
		name = row.get("task_name") or row.get("task_code") or row.get("wbs_name")
		if not name:
			continue
		start = parse_xer_date(
			row.get("target_start_date")
			or row.get("early_start_date")
			or row.get("act_start_date")
			or row.get("restart_date")
		)
		end = parse_xer_date(
			row.get("target_end_date")
			or row.get("early_end_date")
			or row.get("act_end_date")
			or row.get("reend_date")
		)
		dur = row.get("target_drtn_hr_cnt") or row.get("remain_drtn_hr_cnt") or row.get("act_work_qty")
		duration_days = 1
		try:
			if dur:
				duration_days = max(1, int(float(dur) / 8))
		except (TypeError, ValueError):
			pass
		if start and end and duration_days <= 1:
			duration_days = max(1, date_diff_safe(end, start) + 1)
		if start and not end:
			end = add_days(start, duration_days - 1)
		if not start:
			start = getdate()
		if not end:
			end = add_days(start, duration_days - 1)

		pred_ids = pred_map.get(task_id, [])
		pred_names = [task_id_to_name.get(pid) or pid for pid in pred_ids if pid]
		pred_list = row.get("pred_list") or ""
		if not pred_names and pred_list:
			pred_names = [pred_list.split(",")[0].strip()]

		tasks.append(
			{
				"task_id": task_id,
				"task_name": name[:140],
				"start_date": start,
				"end_date": end,
				"duration_days": duration_days,
				"predecessor_task": ", ".join(n for n in pred_names if n)[:140] or None,
				"is_milestone": 1 if (row.get("task_type") or "").upper() in ("TT_MILE", "TT_Mile") else 0,
				"cost_code": (row.get("task_code") or row.get("wbs_id") or "")[:50] or None
	}
		)
	return tasks


def project_schedule_bounds(tasks: list[dict], fallback_start=None, fallback_end=None):
	start = fallback_start
	end = fallback_end
	for task in tasks:
		ts = task.get("start_date")
		te = task.get("end_date")
		if ts and (not start or ts < start):
			start = ts
		if te and (not end or te > end):
			end = te
	if not start:
		start = getdate()
	if not end:
		end = add_days(start, 30)
	return start, end
