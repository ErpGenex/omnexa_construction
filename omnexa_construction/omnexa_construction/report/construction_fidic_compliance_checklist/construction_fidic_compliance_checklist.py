# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_construction.fidic_compliance_checklist import fidic_checklist_for_contract


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("project_contract"):
		frappe.throw(_("Project Contract is required."), title=_("Filters"))

	rows = fidic_checklist_for_contract(filters.project_contract)
	passed = sum(1 for r in rows if r.get("passed"))
	total = len(rows) or 1
	report_summary = [
		{"label": _("Checklist Score"), "value": f"{int(passed / total * 100)
	}%", "indicator": "Blue"
	},
		{"label": _("Passed"), "value": passed, "indicator": "Green"
	},
		{"label": _("Gaps"), "value": total - passed, "indicator": "Red"
	},
	]
	return _columns(), rows, None, None, report_summary


def _columns():
	return [
		{"label": _("Requirement"), "fieldname": "requirement", "fieldtype": "Data", "width": 320
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80
	},
		{"label": _("Pass"), "fieldname": "passed", "fieldtype": "Check", "width": 60
	},
	]
