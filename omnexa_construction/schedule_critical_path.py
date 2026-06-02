# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Critical path method (CPM) for schedule baseline tasks."""

from __future__ import annotations

from frappe.utils import date_diff, flt, getdate


def compute_critical_path(tasks: list[dict]) -> list[str]:
	"""Return task_name list on critical path (zero total float)."""
	if not tasks:
		return []

	by_name = {t["task_name"]: t for t in tasks if t.get("task_name")}
	if not by_name:
		return []

	# Build adjacency from predecessor_task field (optional)
	preds: dict[str, list[str]] = {name: [] for name in by_name}
	for name, row in by_name.items():
		pred = (row.get("predecessor_task") or "").strip()
		if pred and pred in by_name:
			preds[name].append(pred)

	# Forward pass — early start/finish (days from project start)
	project_start = min(getdate(t["start_date"]) for t in by_name.values() if t.get("start_date"))
	es: dict[str, int] = {}
	ef: dict[str, int] = {}
	for name in _topo_sort(by_name, preds):
		row = by_name[name]
		dur = max(1, int(row.get("duration_days") or date_diff(row.get("end_date"), row.get("start_date")) or 1))
		if preds[name]:
			es[name] = max(ef[p] for p in preds[name])
		else:
			es[name] = max(0, date_diff(row.get("start_date"), project_start))
		ef[name] = es[name] + dur

	if not ef:
		return []

	project_end = max(ef.values())
	# Backward pass
	lf: dict[str, int] = {}
	ls: dict[str, int] = {}
	successors: dict[str, list[str]] = {n: [] for n in by_name}
	for name, ps in preds.items():
		for p in ps:
			successors[p].append(name)

	for name in reversed(_topo_sort(by_name, preds)):
		row = by_name[name]
		dur = max(1, int(row.get("duration_days") or date_diff(row.get("end_date"), row.get("start_date")) or 1))
		if successors[name]:
			lf[name] = min(ls[s] for s in successors[name])
		else:
			lf[name] = project_end
		ls[name] = lf[name] - dur

	critical = [name for name in by_name if (ls.get(name, 0) - es.get(name, 0)) <= 0]
	return critical


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
