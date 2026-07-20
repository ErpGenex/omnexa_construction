from __future__ import annotations

import frappe

from omnexa_construction.world_class_mock_audit import run_mock_audit


def execute(filters=None):
	filters = filters or {}
	company = filters.get("company")
	if not company:
		company = frappe.defaults.get_user_default("Company")
	result = run_mock_audit(company, filters.get("branch"))
	columns = [
		{"label": "Domain", "fieldname": "domain", "fieldtype": "Data", "width": 200
	},
		{"label": "Score %", "fieldname": "score", "fieldtype": "Percent", "width": 100
	},
		{"label": "Findings", "fieldname": "findings", "fieldtype": "Data", "width": 400
	},
	]
	data = []
	for row in result.get("domains") or []:
		data.append(
			{
				"domain": row.get("domain"),
				"score": row.get("score"),
				"findings": "; ".join(row.get("findings") or [])
	}
		)
	data.append(
		{
			"domain": "Overall",
			"score": result.get("overall_score"),
			"findings": "Ready" if result.get("certification_ready") else "Gaps remain"
	}
	)
	return columns, data
