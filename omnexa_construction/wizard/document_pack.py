from __future__ import annotations

import csv
import io
import json
import zipfile

import frappe
from frappe import _
from frappe.utils import cint, getdate, now_datetime
from frappe.utils.file_manager import save_file


def export_project_document_pack(setup_name: str, *, include_pdf: int = 1) -> dict:
	"""ZIP export: BOQ, phases, IPC, assignments, summary JSON, optional PDF prints."""
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	buffer = io.BytesIO()
	with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
		zf.writestr("README.txt", _readme(setup))
		zf.writestr("project_summary.json", json.dumps(_summary_dict(setup), indent=2, default=str))
		zf.writestr("boq_lines.csv", _boq_csv(setup))
		zf.writestr("phases.csv", _phases_csv(setup))
		zf.writestr("ipc_plan.csv", _ipc_csv(setup))
		zf.writestr("assignments.csv", _assignments_csv(setup))
		zf.writestr("contract_terms.csv", _contract_terms_csv(setup))
		if setup.project_contract:
			zf.writestr("contract.txt", f"Project Contract: {setup.project_contract}\n")
		if cint(include_pdf):
			for pdf_name, content in _pdf_attachments(setup).items():
				zf.writestr(pdf_name, content)
	buffer.seek(0)
	filename = f"project-pack-{setup.name}-{getdate()}.zip"
	file_doc = save_file(
		filename,
		buffer.getvalue(),
		"Construction Project Setup",
		setup.name,
		is_private=1,
	)
	frappe.db.set_value("Construction Project Setup", setup.name, "document_pack_file", file_doc.file_url)
	return {"file_url": file_doc.file_url, "file_name": filename}


def _readme(setup) -> str:
	return (
		f"Omnexa Construction — Project Document Pack\n"
		f"Setup: {setup.name}\n"
		f"Title: {setup.contract_title}\n"
		f"Generated: {now_datetime()}\n"
	)


def _summary_dict(setup) -> dict:
	return {
		"name": setup.name,
		"contract_title": setup.contract_title,
		"building_type": setup.building_type,
		"boq_template": setup.boq_template,
		"estimated_contract_value": setup.estimated_contract_value,
		"planned_start": str(setup.planned_start or ""),
		"planned_completion": str(setup.planned_completion or ""),
		"project_contract": setup.project_contract,
	}


def _boq_csv(setup) -> str:
	out = io.StringIO()
	w = csv.writer(out)
	w.writerow(["cost_code", "description", "qty", "uom", "planned_cost", "phase", "planned_finish"])
	for r in setup.boq_lines or []:
		if not r.include:
			continue
		w.writerow(
			[
				r.cost_code,
				r.item_description,
				r.quantity,
				r.unit_of_measure,
				r.planned_cost,
				r.phase_code,
				r.planned_finish,
			]
		)
	return out.getvalue()


def _phases_csv(setup) -> str:
	out = io.StringIO()
	w = csv.writer(out)
	w.writerow(["phase_code", "name", "start", "finish", "handover", "weight_percent"])
	for p in setup.phases or []:
		w.writerow(
			[p.phase_code, p.phase_name, p.planned_start, p.planned_finish, p.handover_date, p.weight_percent]
		)
	return out.getvalue()


def _ipc_csv(setup) -> str:
	out = io.StringIO()
	w = csv.writer(out)
	w.writerow(["ipc_number", "phase", "date", "cumulative_percent", "net_amount", "retention_percent"])
	for i in setup.ipc_plan or []:
		w.writerow(
			[
				i.ipc_number,
				i.phase_code,
				i.ipc_date,
				i.cumulative_completion_percent,
				i.net_amount,
				i.retention_percent,
			]
		)
	return out.getvalue()


def _pdf_attachments(setup) -> dict[str, bytes]:
	"""Render standard print formats to PDF bytes for the document pack."""
	out: dict[str, bytes] = {}
	if not setup.name:
		return out
	formats = [
		("Construction Setup — BOQ Schedule", f"boq_schedule_{setup.name}.pdf"),
		("Construction Setup — IPC Schedule", f"ipc_schedule_{setup.name}.pdf"),
		("Construction Setup — Phase Delivery", f"phase_delivery_{setup.name}.pdf"),
	]
	for print_format, filename in formats:
		if not frappe.db.exists("Print Format", print_format):
			continue
		try:
			pdf = frappe.get_print(
				"Construction Project Setup",
				setup.name,
				print_format=print_format,
				as_pdf=True,
			)
			if pdf:
				out[filename] = pdf if isinstance(pdf, bytes) else pdf.encode("utf-8")
		except Exception:
			frappe.log_error(title="Document pack PDF")
	return out


def _assignments_csv(setup) -> str:
	out = io.StringIO()
	w = csv.writer(out)
	w.writerow(["type", "party", "trade", "scope"])
	for a in setup.assignments or []:
		w.writerow([a.assignment_type, a.party, a.trade_package_code, a.scope_notes])
	return out.getvalue()


def _contract_terms_csv(setup) -> str:
	out = io.StringIO()
	w = csv.writer(out)
	w.writerow(["group", "title", "text", "sort_order"])
	for row in sorted(setup.contract_terms or [], key=lambda r: int(r.sort_order or 0)):
		w.writerow([row.clause_group, row.clause_title, row.clause_text, row.sort_order])
	return out.getvalue()
