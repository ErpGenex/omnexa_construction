# Patch to add ISO 19650 metadata to CDE Document

import frappe


def execute():
	"""Add ISO 19650 custom fields to CDE Document"""
	
	# ISO 19650 metadata fields
	iso19650_fields = [
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_stage",
			"fieldtype": "Select",
			"label": "ISO 19650 Stage",
			"insert_after": "document_type",
			"options": "Pre-Contract\nDesign\nConstruction\nHandover\nOperation\nDemolition",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_status",
			"fieldtype": "Select",
			"label": "ISO 19650 Status",
			"insert_after": "iso19650_stage",
			"options": "WIP\nShared\nPublished\nSuperseded\nArchived",
			"read_only": 0,
			"hidden": 0,
			"default": "WIP"
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_classification",
			"fieldtype": "Link",
			"label": "ISO 19650 Classification",
			"insert_after": "iso19650_status",
			"options": "Uniclass 2015",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_spatial_zone",
			"fieldtype": "Data",
			"label": "ISO 19650 Spatial Zone",
			"insert_after": "iso19650_classification",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_work_breakdown",
			"fieldtype": "Data",
			"label": "ISO 19650 Work Breakdown",
			"insert_after": "iso19650_spatial_zone",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_originator",
			"fieldtype": "Data",
			"label": "ISO 19650 Originator",
			"insert_after": "iso19650_work_breakdown",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_discipline",
			"fieldtype": "Select",
			"label": "ISO 19650 Discipline",
			"insert_after": "iso19650_originator",
			"options": "Architecture\nStructural\nMEP\nFire Safety\nAcoustics\nLandscape\nCivil\nOther",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "iso19650_purpose",
			"fieldtype": "Select",
			"label": "ISO 19650 Purpose",
			"insert_after": "iso19650_discipline",
			"options": "Coordination\nDesign\nConstruction\nHandover\nOperation\nRecord",
			"read_only": 0,
			"hidden": 0
		}
	]
	
	# Versioning fields
	versioning_fields = [
		{
			"dt": "Construction CDE Document",
			"fieldname": "version_number",
			"fieldtype": "Int",
			"label": "Version Number",
			"insert_after": "revision",
			"read_only": 1,
			"hidden": 0,
			"default": "1"
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "previous_version",
			"fieldtype": "Link",
			"label": "Previous Version",
			"insert_after": "version_number",
			"options": "Construction CDE Document",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "version_notes",
			"fieldtype": "Text",
			"label": "Version Notes",
			"insert_after": "previous_version",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "is_superseded",
			"fieldtype": "Check",
			"label": "Is Superseded",
			"insert_after": "version_notes",
			"read_only": 1,
			"hidden": 0,
			"default": "0"
		},
		{
			"dt": "Construction CDE Document",
			"fieldname": "superseded_by",
			"fieldtype": "Link",
			"label": "Superseded By",
			"insert_after": "is_superseded",
			"options": "Construction CDE Document",
			"read_only": 1,
			"hidden": 0
		}
	]
	
	# Add custom fields
	for field in iso19650_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	for field in versioning_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	frappe.clear_cache()
