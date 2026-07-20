from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime


def _xml_escape(value: str) -> str:
	return (
		(value or "")
		.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
	)


@frappe.whitelist()
def export_baseline_msp_xml(baseline_name: str) -> dict:
	"""Export schedule baseline tasks to a minimal MS Project XML (MVP)."""
	baseline = frappe.get_doc("Construction Schedule Baseline", baseline_name)
	tasks = baseline.get("tasks") or []
	if not tasks:
		frappe.throw(_("No baseline tasks to export."), title=_("MSP Export"))

	uid = 1
	task_xml = []
	for row in tasks:
		task_xml.append(
			f"""
		<Task>
			<UID>{uid}</UID>
			<Name>{_xml_escape(row.task_name)}</Name>
			<Start>{row.start_date}T08:00:00</Start>
			<Finish>{row.end_date}T17:00:00</Finish>
			<PercentComplete>{int(frappe.utils.flt(row.progress_percent))}</PercentComplete>
		</Task>"""
		)
		uid += 1

	xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
	<Name>{_xml_escape(baseline.baseline_name)}</Name>
	<Tasks>{''.join(task_xml)}
	</Tasks>
</Project>"""

	file_name = f"schedule_{baseline.name}_{now_datetime().strftime('%Y%m%d%H%M%S')}.xml"
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": file_name,
			"content": xml,
			"is_private": 1,
			"attached_to_doctype": "Construction Schedule Baseline",
			"attached_to_name": baseline.name
	}
	)
	file_doc.insert(ignore_permissions=True)
	return {"file_url": file_doc.file_url, "file_name": file_name
	}
