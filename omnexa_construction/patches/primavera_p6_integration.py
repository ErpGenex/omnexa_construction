# Patch to add Primavera P6 custom fields to existing DocTypes

import frappe


def execute():
	"""Add custom fields for Primavera P6 integration"""
	
	# Custom fields for Project Contract
	project_contract_fields = [
		{
			"dt": "Project Contract",
			"fieldname": "p6_project_id",
			"fieldtype": "Data",
			"label": "P6 Project ID",
			"insert_after": "project_name",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Project Contract",
			"fieldname": "p6_project_object_id",
			"fieldtype": "Data",
			"label": "P6 Project Object ID",
			"insert_after": "p6_project_id",
			"read_only": 1,
			"hidden": 1
		},
		{
			"dt": "Project Contract",
			"fieldname": "p6_calendar_id",
			"fieldtype": "Data",
			"label": "P6 Calendar ID",
			"insert_after": "p6_project_object_id",
			"read_only": 0,
			"hidden": 0,
			"default": "Default"
		},
		{
			"dt": "Project Contract",
			"fieldname": "p6_last_sync",
			"fieldtype": "Datetime",
			"label": "P6 Last Sync",
			"insert_after": "p6_calendar_id",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Project Contract",
			"fieldname": "p6_sync_status",
			"fieldtype": "Select",
			"label": "P6 Sync Status",
			"insert_after": "p6_last_sync",
			"options": "Not Synced\nSynced\nSync Failed\nPending",
			"read_only": 1,
			"hidden": 0,
			"default": "Not Synced"
		}
	]
	
	# Custom fields for PM WBS Task
	task_fields = [
		{
			"dt": "PM WBS Task",
			"fieldname": "p6_activity_id",
			"fieldtype": "Data",
			"label": "P6 Activity ID",
			"insert_after": "subject",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "PM WBS Task",
			"fieldname": "p6_activity_object_id",
			"fieldtype": "Data",
			"label": "P6 Activity Object ID",
			"insert_after": "p6_activity_id",
			"read_only": 1,
			"hidden": 1
		},
		{
			"dt": "PM WBS Task",
			"fieldname": "p6_last_sync",
			"fieldtype": "Datetime",
			"label": "P6 Last Sync",
			"insert_after": "p6_activity_object_id",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "PM WBS Task",
			"fieldname": "p6_sync_status",
			"fieldtype": "Select",
			"label": "P6 Sync Status",
			"insert_after": "p6_last_sync",
			"options": "Not Synced\nSynced\nSync Failed\nPending",
			"read_only": 1,
			"hidden": 0,
			"default": "Not Synced"
		}
	]
	
	# Custom fields for Resource
	resource_fields = [
		{
			"dt": "Resource",
			"fieldname": "p6_resource_id",
			"fieldtype": "Data",
			"label": "P6 Resource ID",
			"insert_after": "resource_name",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Resource",
			"fieldname": "p6_resource_object_id",
			"fieldtype": "Data",
			"label": "P6 Resource Object ID",
			"insert_after": "p6_resource_id",
			"read_only": 1,
			"hidden": 1
		},
		{
			"dt": "Resource",
			"fieldname": "p6_last_sync",
			"fieldtype": "Datetime",
			"label": "P6 Last Sync",
			"insert_after": "p6_resource_object_id",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Resource",
			"fieldname": "p6_sync_status",
			"fieldtype": "Select",
			"label": "P6 Sync Status",
			"insert_after": "p6_last_sync",
			"options": "Not Synced\nSynced\nSync Failed\nPending",
			"read_only": 1,
			"hidden": 0,
			"default": "Not Synced"
		}
	]
	
	# Add custom fields
	for field in project_contract_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	for field in task_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	for field in resource_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	frappe.clear_cache()
