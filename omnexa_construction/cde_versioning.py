# CDE Versioning Hooks
# Document event hooks for CDE document versioning

import frappe
from frappe import _
from datetime import datetime


def before_submit_cde_document(doc, method):
	"""Handle versioning before CDE document submission"""
	# Check if this is a new version
	if doc.get('previous_version'):
		# Mark previous version as superseded
		previous_doc = frappe.get_doc('Construction CDE Document', doc.previous_version)
		previous_doc.is_superseded = 1
		previous_doc.superseded_by = doc.name
		previous_doc.iso19650_status = 'Superseded'
		previous_doc.save()
	
	# Set version number
	if not doc.version_number:
		doc.version_number = 1
	
	# Set ISO 19650 status
	if not doc.iso19650_status:
		doc.iso19650_status = 'Published'


def on_update_cde_document(doc, method):
	"""Handle versioning on CDE document update"""
	# Auto-increment version number on significant changes
	if doc.docstatus == 0 and doc.has_value_changed('file') and not doc.version_number:
		# Check if there are existing versions
		existing_versions = frappe.get_all('Construction CDE Document', {
			'project': doc.project,
			'document_type': doc.document_type,
			'docstatus': ['!=', 2]
		}, ['name', 'version_number'], order_by='version_number desc', limit=1)
		
		if existing_versions:
			doc.version_number = existing_versions[0].version_number + 1
		else:
			doc.version_number = 1
