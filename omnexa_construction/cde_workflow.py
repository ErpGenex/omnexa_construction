from __future__ import annotations

import frappe
from frappe import _

CDE_TRANSITIONS = {
	"WIP": {"Shared", "Archived"},
	"Shared": {"Published", "WIP", "Archived"},
	"Published": {"Archived"
	},
	"Archived": set()
	}


def validate_cde_status_transition(old_status: str | None, new_status: str) -> None:
	old_status = old_status or "WIP"
	allowed = CDE_TRANSITIONS.get(old_status, set())
	if new_status != old_status and new_status not in allowed:
		frappe.throw(
			_("CDE status cannot move from {0} to {1}. Allowed: {2}").format(
				old_status, new_status, ", ".join(sorted(allowed)) or "—"
			),
			title=_("CDE Workflow"),
		)


def user_can_publish_cde(user: str | None = None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	return bool(roles & {"System Manager", "Project Manager", "Document Controller"})
