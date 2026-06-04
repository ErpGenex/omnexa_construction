# Primavera P6 Integration Hooks
# Document event hooks for Primavera P6 sync

import frappe
from frappe import _
from datetime import datetime


def set_sync_timestamp(doc, method):
	"""Set sync timestamp for Primavera Integration Log"""
	if not doc.sync_timestamp:
		doc.sync_timestamp = datetime.now()


def set_queue_timestamp(doc, method):
	"""Set queue timestamp for Primavera Sync Queue"""
	if not doc.queue_timestamp:
		doc.queue_timestamp = datetime.now()
	
	if not doc.next_attempt:
		doc.next_attempt = datetime.now()


def queue_project_sync(doc, method):
	"""Queue project sync to P6 on save"""
	settings = frappe.get_single('Primavera P6 Settings')
	if not settings.enabled or not settings.auto_sync_enabled:
		return
	
	# Check if project should be synced
	if not doc.get('p6_project_id') or doc.has_value_changed('name') or doc.has_value_changed('project_name'):
		queue_doc = frappe.new_doc('Primavera Sync Queue')
		queue_doc.entity_type = 'Project'
		queue_doc.entity_id = doc.name
		queue_doc.sync_direction = 'To P6'
		queue_doc.priority = 'Medium'
		queue_doc.insert()


def queue_task_sync(doc, method):
	"""Queue task sync to P6 on save"""
	settings = frappe.get_single('Primavera P6 Settings')
	if not settings.enabled or not settings.auto_sync_enabled:
		return
	
	# Check if task should be synced
	if not doc.get('p6_activity_id') or doc.has_value_changed('subject') or doc.has_value_changed('exp_start_date') or doc.has_value_changed('exp_end_date'):
		queue_doc = frappe.new_doc('Primavera Sync Queue')
		queue_doc.entity_type = 'Task'
		queue_doc.entity_id = doc.name
		queue_doc.sync_direction = 'To P6'
		queue_doc.priority = 'Medium'
		queue_doc.insert()


def queue_resource_sync(doc, method):
	"""Queue resource sync to P6 on save"""
	settings = frappe.get_single('Primavera P6 Settings')
	if not settings.enabled or not settings.auto_sync_enabled:
		return
	
	# Check if resource should be synced
	if not doc.get('p6_resource_id') or doc.has_value_changed('resource_name') or doc.has_value_changed('resource_type'):
		queue_doc = frappe.new_doc('Primavera Sync Queue')
		queue_doc.entity_type = 'Resource'
		queue_doc.entity_id = doc.name
		queue_doc.sync_direction = 'To P6'
		queue_doc.priority = 'Low'
		queue_doc.insert()
