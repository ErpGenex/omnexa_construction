# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""IPC VAT/WHT calculations (testable)."""

from __future__ import annotations

from frappe.utils import flt


def compute_ipc_tax_amounts(
	net_amount: float,
	gross_amount: float,
	vat_percent: float = 0,
	wht_percent: float = 0,
) -> dict:
	vat_amount = flt(gross_amount) * flt(vat_percent) / 100.0 if vat_percent else 0.0
	wht_amount = flt(net_amount) * flt(wht_percent) / 100.0 if wht_percent else 0.0
	net_after_tax = flt(net_amount) + vat_amount - wht_amount
	return {
		"vat_amount": vat_amount,
		"wht_amount": wht_amount,
		"net_after_tax": net_after_tax
	}
