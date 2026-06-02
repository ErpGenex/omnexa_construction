from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import today


def maybe_create_transmittal_for_published_cde(doc) -> str | None:
	"""Auto-create a transmittal line when a CDE document is published (ISO 19650 distribution)."""
	if doc.cde_status != "Published" or not doc.project_contract:
		return None
	transmittal = frappe.get_doc(
		{
			"doctype": "Construction Document Transmittal",
			"project_contract": doc.project_contract,
			"company": doc.company,
			"branch": doc.branch,
			"transmittal_date": today(),
			"issued_by": frappe.session.user,
			"status": "Draft",
			"recipient_notes": _("Auto-generated from CDE publish: {0}").format(doc.name),
		}
	)
	transmittal.append(
		"items",
		{
			"document_no": doc.document_number,
			"document_title": doc.document_title,
			"revision_no": doc.revision,
			"issue_purpose": "For Record",
			"file": doc.file_attachment,
		},
	)
	transmittal.insert(ignore_permissions=True)
	return transmittal.name
