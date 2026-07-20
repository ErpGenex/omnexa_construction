# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from pathlib import Path

import frappe

from omnexa_construction.construction_forms.print_style import ensure_print_format

DOCTYPE = "Construction Project Setup"
MODULE = "Omnexa Construction"

PRINT_FORMATS = (
	("Construction Setup — BOQ Schedule", "setup_boq_schedule.html"),
	("Construction Setup — IPC Schedule", "setup_ipc_schedule.html"),
	("Construction Setup — Phase Delivery", "setup_phase_delivery.html"),
)


def _template_dir() -> Path:
	return Path(__file__).resolve().parents[2] / "wizard" / "print_templates"


def execute():
	if not frappe.db.exists("DocType", DOCTYPE):
		return
	base = _template_dir()
	for name, filename in PRINT_FORMATS:
		html = (base / filename).read_text(encoding="utf-8")
		ensure_print_format(name, DOCTYPE, html)
