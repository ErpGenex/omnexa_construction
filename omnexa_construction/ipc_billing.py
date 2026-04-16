# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""IPC (progress billing) helpers — cumulative % model with period gross."""

from __future__ import annotations

from frappe.utils import flt


def compute_ipc_amounts(
	*,
	billable_contract_value: float,
	cumulative_completion_percent: float,
	prior_certified_completion_percent: float,
	retention_percent: float,
	advance_recovery: float,
) -> dict[str, float]:
	"""Return cumulative billed, prior cumulative, period gross, retention, net.

	``cumulative_completion_percent`` is the **cumulative** completion % on this certificate.
	``prior_certified_completion_percent`` is the cumulative % on the latest **prior** certified IPC.
	"""
	billable = flt(billable_contract_value)
	cur_pct = flt(cumulative_completion_percent)
	prior_pct = flt(prior_certified_completion_percent)
	cur_cum = billable * cur_pct / 100.0
	prior_cum = billable * prior_pct / 100.0
	period_gross = max(0.0, cur_cum - prior_cum)
	retention = period_gross * flt(retention_percent) / 100.0
	net = period_gross - retention - flt(advance_recovery)
	return {
		"cumulative_value_billed": cur_cum,
		"prior_cumulative_billed": prior_cum,
		"gross_amount": period_gross,
		"retention_deduction": retention,
		"net_amount": net,
	}
