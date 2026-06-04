# Primavera P6 Sync Scheduler
# Scheduled task for processing sync queue

import frappe
from frappe import _
from datetime import datetime


def process_sync_queue():
	"""
	Process pending sync queue items
	This function is called hourly by the scheduler
	"""
	try:
		settings = frappe.get_single('Primavera P6 Settings')
		if not settings.enabled:
			return
		
		# Get pending queue items that are due for processing
		now = datetime.now()
		pending_items = frappe.get_all(
			'Primavera Sync Queue',
			filters={
				'status': 'Pending',
				'next_attempt': ['<=', now]
			},
			fields=['name', 'entity_type', 'entity_id', 'sync_direction', 'priority'],
			order_by='priority desc, queue_timestamp asc',
			limit=settings.batch_size or 100
		)
		
		if not pending_items:
			return
		
		frappe.logger.info(f"Processing {len(pending_items)} pending sync queue items")
		
		# Process each item
		for item in pending_items:
			try:
				queue_doc = frappe.get_doc('Primavera Sync Queue', item.name)
				queue_doc.process_sync()
			except Exception as e:
				frappe.log_error(f"Failed to process sync queue item {item.name}: {str(e)}", "Primavera Sync Scheduler")
				continue
		
		frappe.logger.info(f"Completed processing sync queue items")
		
	except Exception as e:
		frappe.log_error(f"Sync scheduler failed: {str(e)}", "Primavera Sync Scheduler")


def cleanup_old_logs():
	"""
	Cleanup old sync logs
	This function is called daily by the scheduler
	"""
	try:
		# Delete logs older than 90 days
		cutoff_date = frappe.utils.add_days(frappe.utils.nowdate(), -90)
		
		old_logs = frappe.get_all(
			'Primavera Integration Log',
			filters={
				'sync_timestamp': ['<', cutoff_date]
			},
			fields=['name'],
			limit=1000
		)
		
		for log in old_logs:
			try:
				frappe.delete_doc('Primavera Integration Log', log.name)
			except Exception as e:
				frappe.logger.warning(f"Failed to delete old log {log.name}: {str(e)}")
		
		frappe.logger.info(f"Cleaned up {len(old_logs)} old sync logs")
		
	except Exception as e:
		frappe.log_error(f"Log cleanup failed: {str(e)}", "Primavera Sync Scheduler")


def cleanup_completed_queue():
	"""
	Cleanup completed sync queue items
	This function is called daily by the scheduler
	"""
	try:
		# Delete completed items older than 30 days
		cutoff_date = frappe.utils.add_days(frappe.utils.nowdate(), -30)
		
		old_items = frappe.get_all(
			'Primavera Sync Queue',
			filters={
				'status': ['in', ['Completed', 'Cancelled']],
				'queue_timestamp': ['<', cutoff_date]
			},
			fields=['name'],
			limit=1000
		)
		
		for item in old_items:
			try:
				frappe.delete_doc('Primavera Sync Queue', item.name)
			except Exception as e:
				frappe.logger.warning(f"Failed to delete old queue item {item.name}: {str(e)}")
		
		frappe.logger.info(f"Cleaned up {len(old_items)} old sync queue items")
		
	except Exception as e:
		frappe.log_error(f"Queue cleanup failed: {str(e)}", "Primavera Sync Scheduler")
