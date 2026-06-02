# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


SUPPORTED_FRAPPE_MAJOR = 15


def enforce_supported_frappe_version():
	"""Fail early when running on an unsupported Frappe major release."""
	version_text = (getattr(frappe, "__version__", "") or "").strip()
	if not version_text:
		return

	major_token = version_text.split(".", 1)[0]
	try:
		major = int(major_token)
	except ValueError:
		return

	if major != SUPPORTED_FRAPPE_MAJOR:
		frappe.throw(
			f"Unsupported Frappe version '{version_text}' for omnexa_construction. "
			"Supported range is >=15.0,<16.0.",
			frappe.ValidationError,
		)


def after_migrate():
	"""Keep wizard building-type Select options aligned with BUILDING_TYPE_META."""
	from omnexa_construction.wizard.building_type_registry import sync_building_type_select_options

	sync_building_type_select_options()
