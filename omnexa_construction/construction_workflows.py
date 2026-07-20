# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Idempotent creation of standard construction commercial workflows."""

from __future__ import annotations

import frappe


def _ensure_workflow_state(state: str) -> None:
	if frappe.db.exists("Workflow State", state):
		return
	frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state, "style": "Primary"}).insert(
		ignore_permissions=True
	)


def _ensure_workflow_action(action: str) -> None:
	if frappe.db.exists("Workflow Action Master", action):
		return
	frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
		ignore_permissions=True
	)


def _state(state, doc_status, *, allow_edit="All", update_field=None, update_value=None, style="Primary"):
	_ensure_workflow_state(state)
	row = {
		"state": state,
		"doc_status": str(doc_status),
		"style": style,
		"allow_edit": allow_edit,
	}
	if update_field:
		row["update_field"] = update_field
		row["update_value"] = update_value
	return row


def _transition(state, action, next_state, allowed="Project Manager"):
	_ensure_workflow_action(action)
	_ensure_workflow_state(state)
	_ensure_workflow_state(next_state)
	return {
		"state": state,
		"action": action,
		"next_state": next_state,
		"allowed": allowed,
		"allow_self_approval": 1,
	}


def ensure_workflow(workflow_name: str, document_type: str, states: list, transitions: list) -> None:
	if not frappe.db.exists("DocType", document_type):
		return
	if frappe.db.exists("Workflow", workflow_name):
		frappe.db.set_value("Workflow", workflow_name, "is_active", 1)
		return

	wf = frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": workflow_name,
			"document_type": document_type,
			"is_active": 1,
			"override_status": 0,
			"workflow_state_field": "workflow_state",
			"send_email_alert": 0,
			"states": states,
			"transitions": transitions,
		}
	)
	wf.insert(ignore_permissions=True)


def sync_all_commercial_workflows() -> list[str]:
	created = []

	ensure_workflow(
		"IPC Certificate Approval",
		"IPC Certificate",
		states=[
			_state("Draft", 0),
			_state("QS Review", 0, allow_edit="Construction QS", style="Warning"),
			_state("Commercial Review", 0, allow_edit="Construction Commercial Manager", style="Warning"),
			_state("PM Approval", 0, allow_edit="Project Manager", style="Info"),
			_state("Certified", 1, allow_edit="System Manager", style="Success", update_field="status", update_value="Certified"),
			_state("Posted", 1, allow_edit="Finance Manager", style="Success", update_field="status", update_value="Posted"),
			_state("Cancelled", 2, allow_edit="System Manager", style="Danger", update_field="status", update_value="Cancelled"),
		],
		transitions=[
			_transition("Draft", "Submit for QS", "QS Review", "Site Engineer"),
			_transition("Draft", "Submit for QS", "QS Review", "Construction QS"),
			_transition("QS Review", "Commercial Review", "Commercial Review", "Construction Commercial Manager"),
			_transition("Commercial Review", "PM Approve", "PM Approval", "Project Manager"),
			_transition("PM Approval", "Certify", "Certified", "Project Manager"),
			_transition("Certified", "Mark Posted", "Posted", "Finance Manager"),
			_transition("Certified", "Cancel", "Cancelled", "Project Manager"),
		],
	)
	created.append("IPC Certificate Approval")

	ensure_workflow(
		"Construction Change Order",
		"Construction Change Order",
		states=[
			_state("Draft", 0),
			_state("Priced", 0, allow_edit="Construction Commercial Manager"),
			_state("Client Approved", 0, allow_edit="Project Manager"),
			_state("Implemented", 1, allow_edit="System Manager", update_field="status", update_value="Implemented"),
			_state("Rejected", 0, allow_edit="System Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Mark Priced", "Priced"),
			_transition("Priced", "Client Approve", "Client Approved"),
			_transition("Client Approved", "Implement", "Implemented"),
			_transition("Priced", "Reject", "Rejected"),
		],
	)
	created.append("Construction Change Order")

	ensure_workflow(
		"Construction Extension of Time",
		"Construction Extension of Time",
		states=[
			_state("Draft", 0),
			_state("Submitted", 0, allow_edit="Project Manager"),
			_state("Assessed", 0, allow_edit="Construction Commercial Manager"),
			_state("Approved", 1, allow_edit="System Manager", update_field="status", update_value="Approved"),
			_state("Rejected", 0, allow_edit="System Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Submit", "Submitted"),
			_transition("Submitted", "Assess", "Assessed"),
			_transition("Assessed", "Approve", "Approved"),
			_transition("Assessed", "Reject", "Rejected"),
		],
	)
	created.append("Construction Extension of Time")

	ensure_workflow(
		"Construction Claim",
		"Construction Claim",
		states=[
			_state("Draft", 0),
			_state("Notified", 0, allow_edit="Construction Commercial Manager"),
			_state("Substantiated", 0, allow_edit="Project Manager"),
			_state("Settled", 1, allow_edit="System Manager", update_field="status", update_value="Accepted"),
			_state("Rejected", 0, allow_edit="System Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Notify", "Notified"),
			_transition("Notified", "Substantiate", "Substantiated"),
			_transition("Substantiated", "Settle", "Settled"),
			_transition("Substantiated", "Reject", "Rejected"),
		],
	)
	created.append("Construction Claim")

	ensure_workflow(
		"Construction Final Account",
		"Construction Final Account Statement",
		states=[
			_state("Draft", 0),
			_state("Reconciled", 0, allow_edit="Construction Commercial Manager"),
			_state("Agreed", 1, allow_edit="System Manager", update_field="status", update_value="Agreed"),
			_state("Closed", 1, allow_edit="System Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Reconcile", "Reconciled"),
			_transition("Reconciled", "Agree", "Agreed"),
			_transition("Agreed", "Close", "Closed"),
		],
	)
	created.append("Construction Final Account")

	ensure_workflow(
		"Subcontract Payment Certificate",
		"Subcontract Payment Certificate",
		states=[
			_state("Draft", 0),
			_state("Site Verified", 0, allow_edit="Site Engineer"),
			_state("Commercial Approved", 0, allow_edit="Construction Commercial Manager"),
			_state("Approved", 1, allow_edit="Finance Manager"),
			_state("Paid", 1, allow_edit="Finance Manager"),
		],
		transitions=[
			_transition("Draft", "Site Verify", "Site Verified", "Site Engineer"),
			_transition("Site Verified", "Commercial Approve", "Commercial Approved", "Construction Commercial Manager"),
			_transition("Commercial Approved", "Approve", "Approved", "Finance Manager"),
			_transition("Approved", "Mark Paid", "Paid", "Finance Manager"),
		],
	)
	created.append("Subcontract Payment Certificate")

	frappe.clear_cache(doctype="Workflow")
	return created


def sync_nec4_and_dispute_workflows() -> list[str]:
	"""NEC4 Early Warning / Compensation Event and dispute workflows."""
	created = []

	ensure_workflow(
		"Construction Early Warning",
		"Construction Early Warning",
		states=[
			_state("Draft", 0),
			_state("Open", 0, allow_edit="Project Manager", update_field="status", update_value="Open"),
			_state("Escalated", 0, allow_edit="Construction Commercial Manager", update_field="status", update_value="Escalated"),
			_state("Closed", 1, allow_edit="System Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Open", "Open", "Site Engineer"),
			_transition("Open", "Escalate", "Escalated", "Project Manager"),
			_transition("Escalated", "Close", "Closed", "Construction Commercial Manager"),
			_transition("Open", "Close", "Closed", "Project Manager"),
		],
	)
	created.append("Construction Early Warning")

	ensure_workflow(
		"Construction Compensation Event",
		"Construction Compensation Event",
		states=[
			_state("Draft", 0),
			_state("Notified", 0, allow_edit="Construction Commercial Manager", update_field="status", update_value="Notified"),
			_state("Quoted", 0, allow_edit="Construction Commercial Manager", update_field="status", update_value="Quoted"),
			_state("Implemented", 1, allow_edit="Project Manager", update_field="status", update_value="Implemented"),
			_state("Rejected", 0, allow_edit="System Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Notify", "Notified"),
			_transition("Notified", "Quote", "Quoted"),
			_transition("Quoted", "Implement", "Implemented"),
			_transition("Quoted", "Reject", "Rejected"),
		],
	)
	created.append("Construction Compensation Event")

	ensure_workflow(
		"Construction Dispute Case",
		"Construction Dispute Case",
		states=[
			_state("Draft", 0),
			_state("Open", 0, allow_edit="Construction Commercial Manager", update_field="status", update_value="Open"),
			_state("DAB Referral", 0, allow_edit="Project Manager", update_field="status", update_value="DAB Referral"),
			_state("Settled", 1, allow_edit="System Manager", update_field="status", update_value="Settled"),
			_state("Closed", 1, allow_edit="System Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Open Case", "Open"),
			_transition("Open", "Refer DAB", "DAB Referral"),
			_transition("DAB Referral", "Settle", "Settled"),
			_transition("Settled", "Close", "Closed"),
		],
	)
	created.append("Construction Dispute Case")

	frappe.clear_cache(doctype="Workflow")
	return created


def sync_qhse_and_document_workflows() -> list[str]:
	created = []

	ensure_workflow(
		"Construction RFI",
		"Construction RFI",
		states=[
			_state("Draft", 0),
			_state("Open", 0, allow_edit="Site Engineer", update_field="status", update_value="Open"),
			_state("Answered", 0, allow_edit="Project Manager", update_field="status", update_value="Answered"),
			_state("Closed", 1, allow_edit="System Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Submit", "Open", "Site Engineer"),
			_transition("Open", "Answer", "Answered", "Project Manager"),
			_transition("Answered", "Close", "Closed", "Construction Document Controller"),
			_transition("Open", "Close", "Closed", "Project Manager"),
		],
	)
	created.append("Construction RFI")

	ensure_workflow(
		"Construction NCR",
		"Construction NCR",
		states=[
			_state("Draft", 0, update_field="status", update_value="Open"),
			_state("Under Review", 0, allow_edit="Construction QA Manager", update_field="status", update_value="Under Review"),
			_state("Closed", 0, allow_edit="Project Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Review", "Under Review", "Construction QA Manager"),
			_transition("Under Review", "Close", "Closed", "Project Manager"),
		],
	)
	created.append("Construction NCR")

	ensure_workflow(
		"Construction CAPA",
		"Construction CAPA",
		states=[
			_state("Draft", 0),
			_state("In Progress", 0, allow_edit="Construction QA Manager", update_field="status", update_value="In Progress"),
			_state("Verified", 0, allow_edit="Project Manager", update_field="status", update_value="Verified"),
			_state("Closed", 1, allow_edit="System Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Start", "In Progress", "Construction QA Manager"),
			_transition("In Progress", "Verify", "Verified", "Project Manager"),
			_transition("Verified", "Close", "Closed", "Construction QA Manager"),
		],
	)
	created.append("Construction CAPA")

	ensure_workflow(
		"Construction Permit to Work",
		"Construction Permit to Work",
		states=[
			_state("Draft", 0),
			_state("Active", 0, allow_edit="Construction HSE Officer", update_field="status", update_value="Active"),
			_state("Expired", 0, allow_edit="System Manager", update_field="status", update_value="Expired", style="Warning"),
			_state("Cancelled", 0, allow_edit="System Manager", update_field="status", update_value="Cancelled", style="Danger"),
		],
		transitions=[
			_transition("Draft", "Activate", "Active", "Construction HSE Officer"),
			_transition("Active", "Expire", "Expired", "Construction HSE Officer"),
			_transition("Active", "Cancel", "Cancelled", "Project Manager"),
		],
	)
	created.append("Construction Permit to Work")

	ensure_workflow(
		"Construction Supplier Prequalification",
		"Construction Supplier Prequalification",
		states=[
			_state("Draft", 0),
			_state("Pending", 0, allow_edit="Construction Commercial Manager", update_field="status", update_value="Pending"),
			_state("Approved", 1, allow_edit="System Manager", update_field="status", update_value="Approved"),
			_state("Rejected", 0, allow_edit="System Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Submit", "Pending", "Cost Controller"),
			_transition("Pending", "Approve", "Approved", "Construction Commercial Manager"),
			_transition("Pending", "Reject", "Rejected", "Construction Commercial Manager"),
		],
	)
	created.append("Construction Supplier Prequalification")

	ensure_workflow(
		"Construction HSE Incident",
		"Construction HSE Incident",
		states=[
			_state("Draft", 0, update_field="status", update_value="Reported"),
			_state("Investigating", 0, allow_edit="Construction HSE Officer", update_field="status", update_value="Investigating"),
			_state("Closed", 0, allow_edit="Project Manager", update_field="status", update_value="Closed"),
		],
		transitions=[
			_transition("Draft", "Investigate", "Investigating", "Construction HSE Officer"),
			_transition("Investigating", "Close", "Closed", "Project Manager"),
		],
	)
	created.append("Construction HSE Incident")

	ensure_workflow(
		"Construction Material Approval Request",
		"Construction Material Approval Request",
		states=[
			_state("Draft", 0, update_field="status", update_value="Draft"),
			_state("Submitted", 0, allow_edit="Site Engineer", update_field="status", update_value="Submitted"),
			_state("Approved", 0, allow_edit="Project Manager", update_field="status", update_value="Approved"),
			_state("Rejected", 0, allow_edit="Project Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Submit", "Submitted", "Site Engineer"),
			_transition("Submitted", "Approve", "Approved", "Project Manager"),
			_transition("Submitted", "Reject", "Rejected", "Project Manager"),
		],
	)
	created.append("Construction Material Approval Request")

	ensure_workflow(
		"Construction Work Approval Request",
		"Construction Work Approval Request",
		states=[
			_state("Draft", 0, update_field="status", update_value="Draft"),
			_state("Submitted", 0, allow_edit="Site Engineer", update_field="status", update_value="Submitted"),
			_state("Approved", 0, allow_edit="Project Manager", update_field="status", update_value="Approved"),
			_state("Rejected", 0, allow_edit="Project Manager", style="Danger", update_field="status", update_value="Rejected"),
		],
		transitions=[
			_transition("Draft", "Submit", "Submitted", "Site Engineer"),
			_transition("Submitted", "Approve", "Approved", "Project Manager"),
			_transition("Submitted", "Reject", "Rejected", "Project Manager"),
		],
	)
	created.append("Construction Work Approval Request")

	frappe.clear_cache(doctype="Workflow")
	return created
