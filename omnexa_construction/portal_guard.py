# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Portal access control for construction application."""

from __future__ import annotations

import frappe
from frappe import _


def extend_bootinfo(bootinfo: dict) -> None:
	"""Extend bootinfo with construction-specific portal data."""
	bootinfo.construction_portal = {
		"enabled": True,
		"workcenter_route": "/app/construction-workcenter",
		"public_site": "/construction",
	}


def enforce_portal_api_access():
	"""Restrict portal API access to authorized users only."""
	# Placeholder for portal access control logic
	# This can be expanded based on specific construction portal requirements
	pass
