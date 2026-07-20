# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Construction module NPS survey."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def submit_nps(score: int, feedback: str | None = None) -> dict:
	score = int(score)
	if score < 0 or score > 10:
		frappe.throw(_("Score must be 0–10."), title=_("NPS"))
	if not frappe.db.exists("DocType", "Construction User NPS"):
		frappe.throw(_("Construction User NPS not installed."), title=_("NPS"))
	doc = frappe.get_doc(
		{
			"doctype": "Construction User NPS",
			"user": frappe.session.user,
			"score": score,
			"feedback": feedback,
			"company": frappe.defaults.get_user_default("Company")
	}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name
	}


@frappe.whitelist()
def get_nps_summary() -> dict:
	if not frappe.db.exists("DocType", "Construction User NPS"):
		return {"nps": None, "responses": 0
	}
	rows = frappe.get_all("Construction User NPS", fields=["score"], limit=1000)
	if not rows:
		return {"nps": None, "responses": 0
	}
	promoters = sum(1 for r in rows if int(r.score) >= 9)
	detractors = sum(1 for r in rows if int(r.score) <= 6)
	n = len(rows)
	nps = round(100 * (promoters - detractors) / n, 1)
	return {"nps": nps, "responses": n, "target": 70, "meets_target": nps >= 70
	}
