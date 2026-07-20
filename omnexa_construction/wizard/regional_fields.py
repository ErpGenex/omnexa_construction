from __future__ import annotations

import re

import frappe
from frappe.utils import flt

_NUMERIC_ONLY = re.compile(r"^[\d.]+$")


def _is_numeric_token(value: str) -> bool:
	return bool(_NUMERIC_ONLY.match(value))


def resolve_regional_cost_factor_name(
	value: str | None,
	*,
	company: str | None = None,
	site_region: str | None = None,
) -> str | None:
	"""Map wizard input to a Regional Cost Factor document name, or None."""
	raw = (value or "").strip()
	if raw and not _is_numeric_token(raw):
		if frappe.db.exists("Regional Cost Factor", raw):
			return raw
		by_code = frappe.db.get_value(
			"Regional Cost Factor",
			{"region_code": raw.upper(), "disabled": 0, **({"company": company} if company else {})},
			"name",
		)
		if by_code:
			return by_code
		autoname = f"RCF-{raw.upper()}"
		if frappe.db.exists("Regional Cost Factor", autoname):
			return autoname

	region = (site_region or "").strip().upper()
	if region:
		filters: dict = {"region_code": region, "disabled": 0}
		if company:
			filters["company"] = company
		name = frappe.db.get_value("Regional Cost Factor", filters, "name")
		if name:
			return name
		autoname = f"RCF-{region}"
		if frappe.db.exists("Regional Cost Factor", autoname):
			return autoname
	return None


def apply_regional_fields(setup, payload: dict) -> None:
	"""Normalize site_region and regional_cost_factor Link before save."""
	site_region = payload.get("site_region")
	if site_region is not None:
		clean_region = (str(site_region) or "").strip().upper()
		setup.site_region = clean_region or None

	raw_factor = payload.get("regional_cost_factor")
	if raw_factor is not None:
		raw_str = (str(raw_factor) or "").strip()
		if not raw_str or _is_numeric_token(raw_str):
			setup.regional_cost_factor = None
		else:
			link = resolve_regional_cost_factor_name(
				raw_str,
				company=setup.company,
				site_region=setup.site_region,
			)
			setup.regional_cost_factor = link
	elif setup.site_region:
		link = resolve_regional_cost_factor_name(
			None,
			company=setup.company,
			site_region=setup.site_region,
		)
		if link:
			setup.regional_cost_factor = link


def effective_regional_multiplier(setup) -> float:
	from omnexa_construction.wizard.regional_cost import resolve_regional_factor

	return resolve_regional_factor(setup)
