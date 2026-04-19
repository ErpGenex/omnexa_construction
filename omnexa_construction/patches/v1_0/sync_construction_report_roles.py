# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

"""Ensure Omnexa Construction script reports are visible on the desk for project and finance roles."""

import frappe

REPORT_NAMES = (
	"BOQ Progress",
	"BOQ Cost Overrun",
	"Construction Contract Control",
	"Construction Contract International Summary",
	"Project Profitability (Construction)",
	"IPC Certificate Summary",
)

ROLES = (
	"System Manager",
	"Company Admin",
	"Desk User",
	"Report Manager",
	"Project Manager",
	"Finance Manager",
	"Cost Controller",
	"Site Engineer",
	"Accounts Manager",
	"Accounts User",
)


def execute():
	valid_roles = set(frappe.get_all("Role", pluck="name"))
	roles = tuple(r for r in ROLES if r in valid_roles)
	if not roles:
		return

	for name in REPORT_NAMES:
		if not frappe.db.exists("Report", name):
			continue
		doc = frappe.get_doc("Report", name)
		doc.roles = []
		for role in roles:
			doc.append("roles", {"role": role})
		doc.save(ignore_permissions=True)

	frappe.clear_cache()
