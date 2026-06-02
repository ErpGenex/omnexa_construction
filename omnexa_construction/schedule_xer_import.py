# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Primavera P6 XER import (MVP — TASK table)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, getdate


@frappe.whitelist()
def import_xer_to_baseline(baseline_name: str, file_url: str) -> dict:
	baseline = frappe.get_doc("Construction Schedule Baseline", baseline_name)
	content = frappe.get_doc("File", {"file_url": file_url}).get_content()
	if isinstance(content, bytes):
		content = content.decode("utf-8", errors="replace")

	tasks = parse_xer_tasks(content)
	if not tasks:
		frappe.throw(_("No tasks found in XER file."), title=_("XER Import"))

	baseline.tasks = []
	project_start = getdate(baseline.planned_start) if baseline.planned_start else getdate()
	for row in tasks:
		start = row.get("start_date") or project_start
		end = row.get("end_date") or add_days(start, max(1, row.get("duration_days", 1) - 1))
		baseline.append(
			"tasks",
			{
				"task_name": row["task_name"],
				"start_date": start,
				"end_date": end,
				"duration_days": row.get("duration_days") or date_diff_safe(end, start) + 1,
				"predecessor_task": row.get("predecessor_task"),
				"is_milestone": row.get("is_milestone") or 0,
			},
		)
	baseline.save()
	return {"imported": len(tasks), "baseline": baseline.name}


def parse_xer_tasks(content: str) -> list[dict]:
	"""Parse XER %T TASK section (tab-delimited)."""
	lines = content.replace("\r\n", "\n").split("\n")
	in_task = False
	fields: list[str] = []
	rows: list[dict] = []

	for line in lines:
		if not line.strip():
			continue
		parts = line.split("\t")
		tag = parts[0]
		if tag == "%T" and len(parts) > 1 and parts[1].strip() == "TASK":
			in_task = True
			fields = []
			continue
		if tag == "%T" and in_task:
			break
		if not in_task:
			continue
		if tag == "%F":
			fields = [p.strip() for p in parts[1:]]
			continue
		if tag == "%R" and fields:
			vals = parts[1:]
			row = dict(zip(fields, vals, strict=False))
			name = row.get("task_name") or row.get("task_code") or row.get("wbs_name")
			if not name:
				continue
			start = row.get("target_start_date") or row.get("early_start_date") or row.get("act_start_date")
			end = row.get("target_end_date") or row.get("early_end_date") or row.get("act_end_date")
			dur = row.get("target_drtn_hr_cnt") or row.get("remain_drtn_hr_cnt")
			duration_days = 1
			try:
				if dur:
					duration_days = max(1, int(float(dur) / 8))
			except (TypeError, ValueError):
				pass
			pred = row.get("pred_list") or ""
			predecessor = pred.split(",")[0].strip() if pred else None
			rows.append(
				{
					"task_name": name[:140],
					"start_date": _parse_xer_date(start),
					"end_date": _parse_xer_date(end),
					"duration_days": duration_days,
					"predecessor_task": predecessor,
					"is_milestone": 1 if (row.get("task_type") or "").upper() == "TT_Mile" else 0,
				}
			)
	return rows


def _parse_xer_date(value: str | None):
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
