# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Critical path method (CPM) for schedule baseline tasks."""

from __future__ import annotations

from frappe.utils import date_diff, getdate


def compute_critical_path(tasks: list[dict]) -> list[str]:
	"""Return task_name list on critical path (zero total float)."""
	if not tasks:
		return []

	by_name = {t["task_name"]: t for t in tasks if t.get("task_name")}
	if not by_name:
		return []

	preds: dict[str, list[str]] = {name: [] for name in by_name}
	for name, row in by_name.items():
		for pred in _resolve_predecessors(row.get("predecessor_task"), by_name):
			if pred not in preds[name]:
				preds[name].append(pred)

	dated = [t for t in by_name.values() if t.get("start_date")]
	if not dated:
		return list(by_name.keys())

	project_start = min(getdate(t["start_date"]) for t in dated)
	es: dict[str, int] = {}
	ef: dict[str, int] = {}
	for name in _topo_sort(by_name, preds):
		row = by_name[name]
		dur = _task_duration(row)
		valid_preds = [p for p in preds.get(name, []) if p in ef]
		if valid_preds:
			es[name] = max(ef[p] for p in valid_preds)
		else:
			es[name] = max(0, date_diff(row.get("start_date"), project_start)) if row.get("start_date") else 0
		ef[name] = es[name] + dur

	if not ef:
		return []

	project_end = max(ef.values())
	successors: dict[str, list[str]] = {n: [] for n in by_name}
	for name, ps in preds.items():
		for p in ps:
			if p in successors:
				successors[p].append(name)

	ls: dict[str, int] = {}
	for name in reversed(_topo_sort(by_name, preds)):
		row = by_name[name]
		dur = _task_duration(row)
		valid_succ = [s for s in successors.get(name, []) if s in ls]
		if valid_succ:
			lf = min(ls[s] for s in valid_succ)
		else:
			lf = project_end
		ls[name] = lf - dur

	return [name for name in by_name if (ls.get(name, 0) - es.get(name, 0)) <= 0]


def _normalize_name(name: str | None) -> str:
	return " ".join((name or "").split())


def _resolve_predecessors(pred_text: str | None, by_name: dict) -> list[str]:
	"""Map predecessor text to known task names; ignore missing/external refs."""
	if not pred_text:
		return []
	lookup = {_normalize_name(k): k for k in by_name}
	resolved: list[str] = []
	for part in str(pred_text).replace(";", ",").split(","):
		key = _normalize_name(part)
		if not key:
			continue
		match = lookup.get(key) or (key if key in by_name else None)
		if match and match not in resolved:
			resolved.append(match)
	return resolved


def _task_duration(row: dict) -> int:
	dur = row.get("duration_days")
	if dur:
		return max(1, int(dur))
	if row.get("start_date") and row.get("end_date"):
		return max(1, date_diff(row.get("end_date"), row.get("start_date")) + 1)
	return 1


def _topo_sort(names: dict, preds: dict) -> list[str]:
	visited: set[str] = set()
	order: list[str] = []

	def visit(n: str):
		if n in visited:
			return
		visited.add(n)
		for p in preds.get(n, []):
			if p in names:
				visit(p)
		order.append(n)

	for n in names:
		visit(n)
	return order
