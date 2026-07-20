# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""EVM-based cost/schedule overrun forecast (rule-based ML v1 — Phase 14.2)."""

from __future__ import annotations

import frappe
from frappe.utils import flt

from omnexa_construction.evm_metrics import evm_snapshot


@frappe.whitelist()
def forecast_overrun(project_contract: str) -> dict:
	snap = evm_snapshot(project_contract)
	bac = flt(snap.get("bac"))
	ac = flt(snap.get("ac"))
	ev = flt(snap.get("ev"))
	pv = flt(snap.get("pv"))
	spi = flt(snap.get("spi")) or 1.0
	cpi = flt(snap.get("cpi")) or 1.0

	eac = ac + (bac - ev) / cpi if cpi else bac
	etc = eac - ac
	vac = bac - eac

	schedule_slip_days = flt(snap.get("schedule_variance_days"))
	finish_slip = schedule_slip_days
	if spi and spi < 1 and bac:
		finish_slip = max(finish_slip, schedule_slip_days / max(spi, 0.01))

	cost_risk = _risk_band(vac, bac)
	schedule_risk = _risk_band(finish_slip, 30, invert=True)

	return {
		"project_contract": project_contract,
		"eac": round(eac, 2),
		"etc": round(etc, 2),
		"vac": round(vac, 2),
		"forecast_finish_slip_days": round(finish_slip, 1),
		"cost_overrun_risk": cost_risk,
		"schedule_overrun_risk": schedule_risk,
		"model": "evm_rule_v1",
		"inputs": {"spi": spi, "cpi": cpi, "bac": bac, "ac": ac, "ev": ev, "pv": pv}
	}


def _risk_band(value: float, scale: float, invert: bool = False) -> str:
	if not scale:
		return "low"
	ratio = abs(value) / scale
	if invert:
		ratio = abs(value) / max(scale, 1)
	if ratio >= 1.0:
		return "high"
	if ratio >= 0.5:
		return "medium"
	return "low"
