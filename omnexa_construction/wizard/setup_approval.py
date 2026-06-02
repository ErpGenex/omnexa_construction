from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt, now

from omnexa_construction.wizard.document_pack import export_project_document_pack
from omnexa_construction.wizard.persist import save_wizard_setup
from omnexa_construction.wizard.pricing import recalculate_setup_pricing
from omnexa_construction.wizard.project_bundle import _bundle_has_submitted_documents, sync_boq_items_from_setup
from omnexa_construction.wizard.setup_contract_terms import suggest_contract_terms


def is_setup_locked(setup) -> bool:
	return (getattr(setup, "approval_status", None) or "Open") == "Approved"


def ensure_setup_editable(setup_name: str) -> frappe.model.document.Document:
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if is_setup_locked(setup):
		frappe.throw(
			_("Setup {0} is approved and locked. Use «Reopen for Revision» to edit.").format(setup_name),
			title=_("Setup Locked"),
		)
	return setup


@frappe.whitelist()
def submit_setup_for_approval(setup_name: str) -> dict:
	setup = ensure_setup_editable(setup_name)
	if setup.status != "Completed":
		frappe.throw(_("Generate the project bundle before submitting for approval."), title=_("Approval"))
	if not setup.boq_lines:
		frappe.throw(_("BOQ lines are required."), title=_("Approval"))
	recalculate_setup_pricing(setup)
	setup.approval_status = "Pending Approval"
	save_wizard_setup(setup)
	return {"approval_status": setup.approval_status}


@frappe.whitelist()
def approve_project_setup(setup_name: str, notes: str | None = None, resync_boq: int | str = 1) -> dict:
	"""Manager approval: lock setup, attach document pack to contract, sync terms & BOQ."""
	frappe.only_for(("Project Manager", "System Manager"), message=_("Only Project Manager can approve setups."))
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.approval_status == "Approved":
		frappe.throw(_("Setup already approved (revision {0}).").format(setup.setup_revision or 1), title=_("Approval"))
	if setup.status != "Completed":
		frappe.throw(_("Complete project generation before approval."), title=_("Approval"))

	recalculate_setup_pricing(setup)
	if not setup.contract_terms:
		suggest_contract_terms(setup)

	pack = export_project_document_pack(setup.name)
	contract_name = setup.project_contract
	resync_result = {}

	if contract_name:
		_sync_contract_header_from_setup(setup, contract_name)
		_copy_terms_to_contract(setup, contract_name)
		_attach_setup_pack_to_contract(setup, contract_name, pack.get("file_url"))
		if cint(resync_boq) and not _bundle_has_submitted_documents(contract_name):
			resync_result = sync_boq_items_from_setup(setup, contract_name)

	setup.approval_status = "Approved"
	setup.approved_by = frappe.session.user
	setup.approved_on = now()
	setup.approval_notes = (notes or "").strip() or None
	if pack.get("file_url"):
		setup.document_pack_file = pack["file_url"]
	setup.flags.approval_unlock = True
	save_wizard_setup(setup)

	return {
		"approval_status": setup.approval_status,
		"setup_revision": setup.setup_revision,
		"project_contract": contract_name,
		"document_pack_file": setup.document_pack_file,
		"resync": resync_result,
	}


@frappe.whitelist()
def reject_project_setup(setup_name: str, notes: str | None = None) -> dict:
	frappe.only_for(("Project Manager", "System Manager"))
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.approval_status == "Approved":
		frappe.throw(_("Cannot reject an approved setup."), title=_("Approval"))
	setup.approval_status = "Rejected"
	setup.approval_notes = (notes or "").strip() or None
	setup.flags.approval_unlock = True
	save_wizard_setup(setup)
	return {"approval_status": setup.approval_status}


@frappe.whitelist()
def reopen_setup_for_revision(setup_name: str, reason: str | None = None) -> dict:
	frappe.only_for(("Project Manager", "System Manager"))
	setup = frappe.get_doc("Construction Project Setup", setup_name)
	if setup.approval_status != "Approved":
		setup.approval_status = "Open"
	else:
		setup.approval_status = "Open"
		setup.setup_revision = cint(setup.setup_revision) + 1
		setup.approved_by = None
		setup.approved_on = None
	setup.approval_notes = (reason or "").strip() or setup.approval_notes
	setup.flags.approval_unlock = True
	save_wizard_setup(setup)
	return {"approval_status": setup.approval_status, "setup_revision": setup.setup_revision}


@frappe.whitelist()
def suggest_setup_contract_terms(setup_name: str, replace: int | str = 0) -> dict:
	setup = ensure_setup_editable(setup_name)
	count = suggest_contract_terms(setup, replace=cint(replace))
	save_wizard_setup(setup)
	return {"terms": len(setup.contract_terms or []), "added": count}


@frappe.whitelist()
def resync_contract_from_setup(setup_name: str) -> dict:
	"""Manual sync of approved/open setup to linked contract (BOQ if no submitted IPCs)."""
	setup = ensure_setup_editable(setup_name)
	if not setup.project_contract:
		frappe.throw(_("No Project Contract linked."), title=_("Sync"))
	recalculate_setup_pricing(setup)
	contract_name = setup.project_contract
	_sync_contract_header_from_setup(setup, contract_name)
	_copy_terms_to_contract(setup, contract_name)
	result = {"contract": contract_name, "boq_resync": {}}
	if not _bundle_has_submitted_documents(contract_name):
		result["boq_resync"] = sync_boq_items_from_setup(setup, contract_name)
	save_wizard_setup(setup)
	return result


def _sync_contract_header_from_setup(setup, contract_name: str) -> None:
	value = sum(flt(r.planned_cost) for r in setup.boq_lines if r.include and not r.is_group)
	payment_terms = _build_payment_terms_text(setup)
	updates = {
		"contract_title": setup.contract_title,
		"contract_type": setup.contract_type,
		"client": setup.client,
		"contract_currency": setup.contract_currency,
		"delivery_model": setup.delivery_model,
		"governing_standard": setup.governing_standard,
		"project_segment": setup.project_segment,
		"building_type": setup.building_type,
		"quality_tier": setup.quality_tier,
		"plot_area_m2": setup.plot_area_m2,
		"gross_floor_area_m2": setup.gross_floor_area_m2,
		"number_of_floors": setup.number_of_floors,
		"basement_levels": setup.basement_levels,
		"unit_count": setup.unit_count,
		"bed_count": setup.bed_count,
		"key_count": setup.key_count,
		"road_length_m": setup.road_length_m,
		"road_width_m": setup.road_width_m,
		"pipe_network_km": setup.pipe_network_km,
		"planned_start": setup.planned_start,
		"planned_completion": setup.planned_completion,
		"site_location": setup.site_location,
		"contract_value": value,
		"revised_contract_value": value,
		"retention_percent": flt(setup.retention_percent) or 5,
		"advance_payment": flt(setup.advance_payment_amount),
		"liquidated_damages_per_day": flt(setup.liquidated_damages_per_day),
		"liquidated_damages_cap_percent": flt(setup.liquidated_damages_cap_percent),
		"payment_terms": payment_terms,
		"wizard_setup": setup.name,
		"approved_setup_revision": cint(setup.setup_revision) or 1,
	}
	frappe.db.set_value("Project Contract", contract_name, updates, update_modified=True)


def _build_payment_terms_text(setup) -> str:
	lines = [
		_("IPC schedule: {0} certificates").format(len(setup.ipc_plan or [])),
		_("Retention: {0}%").format(flt(setup.retention_percent) or 5),
	]
	if setup.advance_payment_percent or setup.advance_payment_amount:
		lines.append(
			_("Advance: {0}% / {1}").format(
				flt(setup.advance_payment_percent),
				setup.advance_payment_amount or "—",
			)
		)
	if setup.default_discount_percent:
		lines.append(_("IPC discount: {0}%").format(flt(setup.default_discount_percent)))
	return "\n".join(lines)


def _copy_terms_to_contract(setup, contract_name: str) -> None:
	contract = frappe.get_doc("Project Contract", contract_name)
	contract.set("contract_terms", [])
	for row in sorted(setup.contract_terms or [], key=lambda r: cint(r.sort_order)):
		contract.append(
			"contract_terms",
			{
				"clause_group": row.clause_group,
				"clause_title": row.clause_title,
				"clause_text": row.clause_text,
				"sort_order": row.sort_order,
			},
		)
	contract.flags.ignore_permissions = True
	if contract.docstatus == 1:
		contract.save(ignore_version=True)
	else:
		contract.save()


def _attach_setup_pack_to_contract(setup, contract_name: str, file_url: str | None) -> None:
	if not file_url:
		return
	frappe.db.set_value(
		"Project Contract",
		contract_name,
		"approved_setup_attachment",
		file_url,
		update_modified=True,
	)
