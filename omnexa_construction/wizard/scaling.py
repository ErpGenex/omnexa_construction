from __future__ import annotations

import ast
import operator as op
from typing import Any

import frappe
from frappe.utils import flt

QUALITY_MULTIPLIERS = {
	"Economy": 0.85,
	"Standard": 1.0,
	"Premium": 1.18,
	"Luxury": 1.35,
}

LUMP_SUM_UOMS = frozenset({"ls", "lot", "item", "no", "l.s.", "lump sum"})
AREA_DRIVERS = frozenset({"GFA", "PLOT", "FLOORS", "UNITS"})

_ALLOWED_OPS = {
	ast.Add: op.add,
	ast.Sub: op.sub,
	ast.Mult: op.mul,
	ast.Div: op.truediv,
	ast.Pow: op.pow,
	ast.USub: op.neg,
}


def quality_multiplier(tier: str | None) -> float:
	return QUALITY_MULTIPLIERS.get(tier or "Standard", 1.0)


def build_drivers(setup) -> dict[str, float]:
	"""Numeric drivers from Construction Project Setup for parametric BOQ."""
	gfa = flt(setup.gross_floor_area_m2)
	plot = flt(setup.plot_area_m2)
	floors = flt(setup.number_of_floors) or 1.0
	units = flt(setup.unit_count) or 1.0
	road_m = flt(setup.road_length_m)
	road_km = road_m / 1000.0 if road_m else 0.0
	pipe_km = flt(setup.pipe_network_km)
	keys = flt(getattr(setup, "key_count", None)) or units
	beds = flt(getattr(setup, "bed_count", None)) or max(units, 1)
	return {
		"gross_floor_area_m2": gfa,
		"GFA": gfa,
		"plot_area_m2": plot,
		"PLOT": plot,
		"number_of_floors": floors,
		"FLOORS": floors,
		"unit_count": units,
		"UNITS": units,
		"key_count": keys,
		"KEY_COUNT": keys,
		"bed_count": beds,
		"BED_COUNT": beds,
		"road_length_m": road_m,
		"ROAD_M": road_m,
		"road_km": road_km,
		"ROAD_KM": road_km,
		"pipe_network_km": pipe_km,
		"PIPE_KM": pipe_km,
		"basement_levels": flt(setup.basement_levels),
	}


def resolve_quantity(line, drivers: dict[str, float], regional_factor: float = 1.0) -> float:
	"""Resolve BOQ quantity from template line driver."""
	driver = (line.get("quantity_driver") if isinstance(line, dict) else line.quantity_driver) or "FIXED"
	base_qty = flt(line.get("base_quantity") if isinstance(line, dict) else line.base_quantity) or 1.0
	formula = line.get("driver_formula") if isinstance(line, dict) else line.driver_formula
	uom = (
		(line.get("unit_of_measure") if isinstance(line, dict) else getattr(line, "unit_of_measure", None))
		or ""
	).strip().lower()

	if driver in AREA_DRIVERS and uom in LUMP_SUM_UOMS:
		driver = "FIXED"

	if driver == "FIXED":
		qty = base_qty
	elif driver == "GFA":
		qty = base_qty * flt(drivers.get("GFA"))
	elif driver == "PLOT":
		qty = base_qty * flt(drivers.get("PLOT"))
	elif driver == "FLOORS":
		qty = base_qty * flt(drivers.get("FLOORS"))
	elif driver == "UNITS":
		qty = base_qty * flt(drivers.get("UNITS"))
	elif driver == "ROAD_M":
		qty = base_qty * flt(drivers.get("ROAD_M"))
	elif driver == "ROAD_KM":
		qty = base_qty * flt(drivers.get("ROAD_KM"))
	elif driver == "PIPE_KM":
		qty = base_qty * flt(drivers.get("PIPE_KM"))
	elif driver == "FORMULA" and formula:
		qty = base_qty * _safe_eval_formula(formula, drivers)
	else:
		qty = base_qty

	return flt(qty) * flt(regional_factor)


def unit_cost_with_quality(unit_cost_base: float, quality_tier: str | None) -> float:
	return flt(unit_cost_base) * quality_multiplier(quality_tier)


def line_planned_cost(qty: float, unit_cost: float) -> float:
	return flt(qty) * flt(unit_cost)


def split_costs(planned: float, labor_ratio=40, material_ratio=50, equipment_ratio=10) -> tuple[float, float, float]:
	total_ratio = flt(labor_ratio) + flt(material_ratio) + flt(equipment_ratio) or 100.0
	return (
		planned * flt(labor_ratio) / total_ratio,
		planned * flt(material_ratio) / total_ratio,
		planned * flt(equipment_ratio) / total_ratio,
	)


def _safe_eval_formula(formula: str, drivers: dict[str, float]) -> float:
	"""Evaluate a small arithmetic formula using driver names only."""
	allowed_names = {k: flt(v) for k, v in drivers.items()}
	node = ast.parse(formula.strip(), mode="eval")

	def _eval(n: ast.AST) -> float:
		if isinstance(n, ast.Expression):
			return _eval(n.body)
		if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
			return flt(n.value)
		if isinstance(n, ast.Name):
			if n.id not in allowed_names:
				frappe.throw(f"Unknown driver in formula: {n.id}")
			return allowed_names[n.id]
		if isinstance(n, ast.BinOp):
			op_fn = _ALLOWED_OPS.get(type(n.op))
			if not op_fn:
				frappe.throw("Unsupported operator in driver formula")
			return op_fn(_eval(n.left), _eval(n.right))
		if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
			return _eval(n.operand) * -1
		frappe.throw("Invalid driver formula")

	return flt(_eval(node))


def rollup_setup_boq_lines(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
	"""Roll group planned costs from included children."""
	by_code = {r["cost_code"]: r for r in lines}
	for row in lines:
		if not row.get("is_group"):
			qty = flt(row.get("quantity"))
			uc = flt(row.get("unit_cost"))
			row["planned_cost"] = line_planned_cost(qty, uc)
	for row in lines:
		if not row.get("is_group"):
			continue
		children = [
			c
			for c in lines
			if c.get("parent_cost_code") == row.get("cost_code") and c.get("include", 1)
		]
		if children:
			row["planned_cost"] = sum(flt(c.get("planned_cost")) for c in children)
	return lines
