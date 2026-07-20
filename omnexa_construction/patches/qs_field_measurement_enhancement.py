# Patch to add mobile app enhancements to QS Field Measurement

import frappe


def execute():
	"""Add mobile app enhancements to QS Field Measurement"""
	
	# Mobile app fields for QS Measurement Sheet
	qs_measurement_fields = [
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "gps_location",
			"fieldtype": "Geolocation",
			"label": "GPS Location",
			"insert_after": "location",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "photo_verification",
			"fieldtype": "Attach Image",
			"label": "Photo Verification",
			"insert_after": "gps_location",
			"read_only": 0,
			"hidden": 0
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "photo_timestamp",
			"fieldtype": "Datetime",
			"label": "Photo Timestamp",
			"insert_after": "photo_verification",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "offline_mode",
			"fieldtype": "Check",
			"label": "Offline Mode",
			"insert_after": "photo_timestamp",
			"read_only": 0,
			"hidden": 0,
			"default": "0"
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "sync_status",
			"fieldtype": "Select",
			"label": "Sync Status",
			"insert_after": "offline_mode",
			"options": "Synced\nPending\nFailed",
			"read_only": 1,
			"hidden": 0,
			"default": "Synced"
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "ocr_extracted_text",
			"fieldtype": "Text",
			"label": "OCR Extracted Text",
			"insert_after": "sync_status",
			"read_only": 1,
			"hidden": 0
		},
		{
			"dt": "Construction QS Measurement Sheet",
			"fieldname": "ocr_confidence",
			"fieldtype": "Percent",
			"label": "OCR Confidence",
			"insert_after": "ocr_extracted_text",
			"read_only": 1,
			"hidden": 0
		}
	]
	
	# Add custom fields
	for field in qs_measurement_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc({
				"doctype": "Custom Field",
				**field
			}).insert()
	
	frappe.clear_cache()
