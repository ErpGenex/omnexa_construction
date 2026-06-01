# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Site Region Code options — ISO country codes + company Regional Cost Factors."""

from __future__ import annotations

from functools import lru_cache

import frappe


def _arabic_country_name(iso_code: str, fallback: str) -> str:
	try:
		from babel import Locale

		locale = Locale.parse("ar")
		return locale.territories.get(iso_code.upper(), fallback) or fallback
	except Exception:
		return fallback


@lru_cache(maxsize=1)
def _iso_country_rows() -> tuple[dict, ...]:
	"""All ISO 3166-1 alpha-2 codes from Frappe country_info."""
	from frappe.geo.country_info import get_all

	rows: list[dict] = []
	seen: set[str] = set()
	for country_name, info in get_all().items():
		info = info or {}
		code = (info.get("code") or "").strip().upper()
		if len(code) != 2 or not code.isalpha() or code in seen:
			continue
		seen.add(code)
		rows.append(
			{
				"region_code": code,
				"region_name": country_name,
				"region_name_ar": _arabic_country_name(code, country_name),
				"source": "country",
			}
		)
	rows.sort(key=lambda r: r["region_name"])
	return tuple(rows)


def get_site_region_options(
	company: str | None = None,
	search: str | None = None,
	*,
	limit: int = 500,
) -> list[dict]:
	"""Merged country ISO codes and company regional cost factor codes."""
	merged: dict[str, dict] = {}
	for row in _iso_country_rows():
		merged[row["region_code"]] = dict(row)

	if company:
		for row in frappe.get_all(
			"Regional Cost Factor",
			filters={"company": company, "disabled": 0},
			fields=["region_code", "region_name", "cost_factor", "is_default"],
			order_by="is_default desc, region_code asc",
		):
			code = (row.region_code or "").strip().upper()
			if not code:
				continue
			merged[code] = {
				"region_code": code,
				"region_name": row.region_name or code,
				"region_name_ar": row.region_name or code,
				"source": "regional",
				"cost_factor": row.cost_factor,
				"is_default": row.is_default,
			}

	out = list(merged.values())
	q = (search or "").strip().lower()
	if q:
		filtered = []
		for row in out:
			hay = " ".join(
				[
					row.get("region_code") or "",
					row.get("region_name") or "",
					row.get("region_name_ar") or "",
				]
			).lower()
			if q in hay:
				filtered.append(row)
		out = filtered

	out.sort(key=lambda r: (0 if r.get("source") == "country" else 1, r.get("region_name") or r["region_code"]))
	if limit and len(out) > limit:
		return out[:limit]
	return out
