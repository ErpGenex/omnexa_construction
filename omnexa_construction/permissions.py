from omnexa_core.omnexa_core.branch_access import (
	enforce_branch_access,
	permission_query_conditions_for_branch_field,
)
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
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
