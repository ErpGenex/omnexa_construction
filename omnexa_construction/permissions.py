from omnexa_core.omnexa_core.branch_access import (
	enforce_branch_access,
	permission_query_conditions_for_branch_field,
)
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
	if getattr(getattr(doc, "flags", None), "wizard_save", False):
		return
	enforce_branch_access(doc)


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def project_contract_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Project Contract", user)


def boq_item_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("BOQ Item", user)


def ipc_certificate_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("IPC Certificate", user)


def site_daily_report_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Site Daily Report", user)


def subcontract_work_order_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Subcontract Work Order", user)


def project_wip_snapshot_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Project WIP Snapshot", user)


def subcontract_payment_certificate_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Subcontract Payment Certificate", user)


def construction_change_order_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Change Order", user)


def construction_extension_of_time_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Extension of Time", user)


def construction_claim_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Claim", user)


def construction_inspection_request_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Inspection Request", user)


def construction_ncr_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction NCR", user)


def construction_hse_incident_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction HSE Incident", user)


def construction_document_transmittal_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Document Transmittal", user)


def construction_project_setup_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Project Setup", user)


def regional_cost_factor_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Regional Cost Factor", user)


def construction_plot_unit_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Plot Unit", user)


def construction_residential_unit_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Residential Unit", user)


def construction_qs_measurement_sheet_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction QS Measurement Sheet", user)


def construction_fidic_notice_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction FIDIC Notice", user)


def construction_final_account_statement_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Final Account Statement", user)


def construction_dlp_record_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction DLP Record", user)


def construction_inspection_test_plan_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Inspection Test Plan", user)


def construction_equipment_usage_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction Equipment Usage", user)


def construction_cde_document_query_conditions(user=None):
	return permission_query_conditions_for_branch_field("Construction CDE Document", user)
