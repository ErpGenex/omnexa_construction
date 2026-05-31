app_name = "omnexa_construction"
app_title = "ErpGenEx — Construction"
app_publisher = "ErpGenEx"
app_description = "Construction management vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "omnexa_construction",
# 		"logo": "/assets/omnexa_construction/logo.png",
# 		"title": "Omnexa Construction",
# 		"route": "/omnexa_construction",
# 		"has_permission": "omnexa_construction.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_construction/css/omnexa_construction.css"
# app_include_js = "/assets/omnexa_construction/js/omnexa_construction.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_construction/css/omnexa_construction.css"
# web_include_js = "/assets/omnexa_construction/js/omnexa_construction.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_construction/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# Company demo buttons: omnexa_core/public/js/company_demo_data_hub.js
doctype_js = {
	"Project Contract": "public/js/project_contract.js",
	"Subcontract Payment Certificate": "public/js/subcontract_payment_certificate.js",
	"IPC Certificate": "public/js/ipc_certificate.js",
	"Construction Project Setup": "public/js/construction_project_setup.js",
	"Construction RFQ": "public/js/construction_rfq.js",
	"Contractor Account Statement": "public/js/contractor_account_statement.js",
	"Construction QS Measurement Sheet": "public/js/construction_qs_measurement_sheet.js",
	"Construction Final Account Statement": "public/js/construction_final_account_statement.js",
	"Site Daily Report": "public/js/site_daily_report.js",
	"Project WIP Snapshot": "public/js/project_wip_snapshot.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_construction/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_construction.utils.jinja_methods",
# 	"filters": "omnexa_construction.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "omnexa_construction.install.enforce_supported_frappe_version"
before_migrate = "omnexa_construction.install.enforce_supported_frappe_version"

# Uninstallation
# ------------

# before_uninstall = "omnexa_construction.uninstall.before_uninstall"
# after_uninstall = "omnexa_construction.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_construction.utils.before_app_install"
# after_app_install = "omnexa_construction.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_construction.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_construction.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_construction.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Project Contract": "omnexa_construction.permissions.project_contract_query_conditions",
	"BOQ Item": "omnexa_construction.permissions.boq_item_query_conditions",
	"IPC Certificate": "omnexa_construction.permissions.ipc_certificate_query_conditions",
	"Site Daily Report": "omnexa_construction.permissions.site_daily_report_query_conditions",
	"Subcontract Work Order": "omnexa_construction.permissions.subcontract_work_order_query_conditions",
	"Project WIP Snapshot": "omnexa_construction.permissions.project_wip_snapshot_query_conditions",
	"Subcontract Payment Certificate": "omnexa_construction.permissions.subcontract_payment_certificate_query_conditions",
	"Construction Change Order": "omnexa_construction.permissions.construction_change_order_query_conditions",
	"Construction Extension of Time": "omnexa_construction.permissions.construction_extension_of_time_query_conditions",
	"Construction Claim": "omnexa_construction.permissions.construction_claim_query_conditions",
	"Construction Inspection Request": "omnexa_construction.permissions.construction_inspection_request_query_conditions",
	"Construction NCR": "omnexa_construction.permissions.construction_ncr_query_conditions",
	"Construction HSE Incident": "omnexa_construction.permissions.construction_hse_incident_query_conditions",
	"Construction Document Transmittal": "omnexa_construction.permissions.construction_document_transmittal_query_conditions",
	"Construction Project Setup": "omnexa_construction.permissions.construction_project_setup_query_conditions",
	"Regional Cost Factor": "omnexa_construction.permissions.regional_cost_factor_query_conditions",
	"Construction Plot Unit": "omnexa_construction.permissions.construction_plot_unit_query_conditions",
	"Construction Residential Unit": "omnexa_construction.permissions.construction_residential_unit_query_conditions",
	"Construction QS Measurement Sheet": "omnexa_construction.permissions.construction_qs_measurement_sheet_query_conditions",
	"Construction FIDIC Notice": "omnexa_construction.permissions.construction_fidic_notice_query_conditions",
	"Construction Final Account Statement": "omnexa_construction.permissions.construction_final_account_statement_query_conditions",
	"Construction DLP Record": "omnexa_construction.permissions.construction_dlp_record_query_conditions",
	"Construction Inspection Test Plan": "omnexa_construction.permissions.construction_inspection_test_plan_query_conditions",
	"Construction Equipment Usage": "omnexa_construction.permissions.construction_equipment_usage_query_conditions",
	"Construction CDE Document": "omnexa_construction.permissions.construction_cde_document_query_conditions",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

_BRANCH_DOC_EVENTS = {
	"before_validate": "omnexa_construction.permissions.populate_company_branch_from_user_context",
	"validate": "omnexa_construction.permissions.enforce_branch_access_for_doc",
}

_WORKFLOW_VALIDATE = [
	"omnexa_construction.permissions.enforce_branch_access_for_doc",
	"omnexa_construction.workflow_hooks.validate_construction_workflow_binding",
]

_COST_ROLLUP_EVENTS = {
	"after_insert": "omnexa_construction.cost_rollup.refresh_linked_boq_actual_cost",
	"on_update": "omnexa_construction.cost_rollup.refresh_linked_boq_actual_cost",
	"on_trash": "omnexa_construction.cost_rollup.refresh_linked_boq_actual_cost",
}

_SITE_DAILY_EVENTS = {
	**_BRANCH_DOC_EVENTS,
	**_COST_ROLLUP_EVENTS,
}

_EQUIPMENT_USAGE_EVENTS = {
	**_BRANCH_DOC_EVENTS,
	**_COST_ROLLUP_EVENTS,
}

_TIMESHEET_EVENTS = {
	"validate": "omnexa_construction.timesheet_cost_hooks.timesheet_entry_before_save",
	**_COST_ROLLUP_EVENTS,
}

_IPC_EVENTS = {
	"before_validate": _BRANCH_DOC_EVENTS["before_validate"],
	"validate": _WORKFLOW_VALIDATE,
	"on_update": "omnexa_construction.ipc_revenue.maybe_create_draft_sales_invoice",
}

doc_events = {
	"Project Contract": _BRANCH_DOC_EVENTS.copy(),
	"BOQ Item": _BRANCH_DOC_EVENTS.copy(),
	"IPC Certificate": _IPC_EVENTS,
	"Site Daily Report": _SITE_DAILY_EVENTS,
	"Subcontract Work Order": _BRANCH_DOC_EVENTS.copy(),
	"Project WIP Snapshot": _BRANCH_DOC_EVENTS.copy(),
	"Subcontract Payment Certificate": {
		"before_validate": _BRANCH_DOC_EVENTS["before_validate"],
		"validate": _WORKFLOW_VALIDATE,
	},
	"Construction Change Order": {
		"before_validate": _BRANCH_DOC_EVENTS["before_validate"],
		"validate": _WORKFLOW_VALIDATE,
	},
	"Construction Extension of Time": _BRANCH_DOC_EVENTS.copy(),
	"Construction Claim": _BRANCH_DOC_EVENTS.copy(),
	"Construction Inspection Request": _BRANCH_DOC_EVENTS.copy(),
	"Construction NCR": _BRANCH_DOC_EVENTS.copy(),
	"Construction HSE Incident": _BRANCH_DOC_EVENTS.copy(),
	"Construction Document Transmittal": _BRANCH_DOC_EVENTS.copy(),
	"Construction Project Setup": _BRANCH_DOC_EVENTS.copy(),
	"Regional Cost Factor": _BRANCH_DOC_EVENTS.copy(),
	"Construction Plot Unit": _BRANCH_DOC_EVENTS.copy(),
	"Construction Residential Unit": _BRANCH_DOC_EVENTS.copy(),
	"Construction QS Measurement Sheet": _BRANCH_DOC_EVENTS.copy(),
	"Construction FIDIC Notice": _BRANCH_DOC_EVENTS.copy(),
	"Construction Final Account Statement": _BRANCH_DOC_EVENTS.copy(),
	"Construction DLP Record": _BRANCH_DOC_EVENTS.copy(),
	"Construction Inspection Test Plan": _BRANCH_DOC_EVENTS.copy(),
	"Construction Equipment Usage": _EQUIPMENT_USAGE_EVENTS,
	"Construction CDE Document": _BRANCH_DOC_EVENTS.copy(),
	"Construction Work Delay Notice": _BRANCH_DOC_EVENTS.copy(),
	"Timesheet Entry": _TIMESHEET_EVENTS,
	"Purchase Request": {
		"validate": "omnexa_construction.procurement_hooks.validate_purchase_request_boq_links",
	},
	"Purchase Order": {
		"validate": "omnexa_construction.procurement_hooks.validate_purchase_order_boq_links",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": ["omnexa_construction.fidic_alerts.mark_overdue_fidic_notices"],
}

# scheduler_events = {
# 	"all": [
# 		"omnexa_construction.tasks.all"
# 	],
# 	"daily": [
# 		"omnexa_construction.tasks.daily"
# 	],
# 	"hourly": [
# 		"omnexa_construction.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omnexa_construction.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omnexa_construction.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "omnexa_construction.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_construction.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_construction.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["omnexa_construction.license_gate.before_request"]
# after_request = ["omnexa_construction.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_construction.utils.before_job"]
# after_job = ["omnexa_construction.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_construction.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

