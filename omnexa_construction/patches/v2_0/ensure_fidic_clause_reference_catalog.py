"""Seed FIDIC/NEC clause references for notices."""

from __future__ import annotations

import frappe


SEED_ROWS = [
	{
		"display_reference": "FIDIC 20.2.1 — Notice of Claim",
		"clause_code": "20.2.1",
		"standard_family": "FIDIC",
		"notice_type": "Claim",
		"time_bar_days": 28,
		"title": "Notice of Claim",
		"description": "Primary time-bar notice for claims under FIDIC 2017."
	},
	{
		"display_reference": "FIDIC 8.4 — Extension of Time for Completion",
		"clause_code": "8.4",
		"standard_family": "FIDIC",
		"notice_type": "Extension of Time",
		"time_bar_days": 28,
		"title": "Extension of Time for Completion",
		"description": "Reference for EOT submissions and responses."
	},
	{
		"display_reference": "FIDIC 13.1 — Right to Vary",
		"clause_code": "13.1",
		"standard_family": "FIDIC",
		"notice_type": "Variation",
		"time_bar_days": 28,
		"title": "Right to Vary",
		"description": "Variation instruction and valuation reference."
	},
	{
		"display_reference": "FIDIC 11.1 — Completion of Outstanding Work and Remedying Defects",
		"clause_code": "11.1",
		"standard_family": "FIDIC",
		"notice_type": "Defects",
		"time_bar_days": 28,
		"title": "Defects and Remedying",
		"description": "Defect notice and remedial tracking reference."
	},
	{
		"display_reference": "FIDIC 14.3 — Application for Interim Payment Certificates",
		"clause_code": "14.3",
		"standard_family": "FIDIC",
		"notice_type": "Payment",
		"time_bar_days": 28,
		"title": "Interim Payment Application",
		"description": "Payment notice and certification cycle reference."
	},
	{
		"display_reference": "FIDIC 15.2 — Termination by Employer",
		"clause_code": "15.2",
		"standard_family": "FIDIC",
		"notice_type": "Termination",
		"time_bar_days": 28,
		"title": "Termination by Employer",
		"description": "Employer termination notice pathway."
	},
	{
		"display_reference": "NEC4 61.3 — Notification of Compensation Event",
		"clause_code": "61.3",
		"standard_family": "NEC4",
		"notice_type": "Claim",
		"time_bar_days": 56,
		"title": "Notification of Compensation Event",
		"description": "NEC4 notification time-bar for compensation events."
	},
	{
		"display_reference": "NEC4 16.1 — Early Warning",
		"clause_code": "16.1",
		"standard_family": "NEC4",
		"notice_type": "Other",
		"time_bar_days": 42,
		"title": "Early Warning",
		"description": "NEC4 early warning trigger for risk mitigation."
	},
]


def execute():
	if not frappe.db.exists("DocType", "Construction FIDIC Clause Reference"):
		return

	for row in SEED_ROWS:
		name = frappe.db.get_value(
			"Construction FIDIC Clause Reference",
			{"display_reference": row["display_reference"]
	},
		)
		if name:
			doc = frappe.get_doc("Construction FIDIC Clause Reference", name)
			doc.update(row)
			doc.flags.ignore_validate_update_after_submit = True
			doc.save(ignore_permissions=True)
			continue
		doc = frappe.get_doc({"doctype": "Construction FIDIC Clause Reference", **row})
		doc.insert(ignore_permissions=True)

	frappe.db.commit()
