# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

from pathlib import Path

import frappe

from omnexa_construction.construction_forms.print_style import ensure_print_format

MODULE = "Omnexa Construction"


def execute():
	base = Path(__file__).resolve().parents[2] / "wizard" / "print_templates"
	_prints = (
		(
			"Project Contract — Summary",
			"Project Contract",
			"""<h2>{{ doc.contract_title or doc.name }}</h2>
<p><b>{{ _("Client") }}:</b> {{ doc.client }} | <b>{{ _("Value") }}:</b> {{ doc.contract_value }} {{ doc.contract_currency }}</p>
<p><b>{{ _("Building") }}:</b> {{ doc.building_type }} | <b>{{ _("GFA") }}:</b> {{ doc.gross_floor_area_m2 }} m²</p>
<p><b>{{ _("Planned") }}:</b> {{ doc.planned_start }} → {{ doc.planned_completion }}</p>""",
		),
		(
			"BOQ Item — Schedule Tree",
			"BOQ Item",
			"""<h3>{{ doc.item_description }}</h3>
<p>{{ doc.cost_code }} · {{ doc.quantity }} {{ doc.unit_of_measure }} · {{ doc.planned_cost }}</p>""",
		),
	)
	for name, doctype, html in _prints:
		if not frappe.db.exists("DocType", doctype):
			continue
		tpl = base / "setup_boq_schedule.html"
		if name.startswith("Construction Setup") and tpl.exists():
			html = tpl.read_text(encoding="utf-8")
		ensure_print_format(name, doctype, html)
