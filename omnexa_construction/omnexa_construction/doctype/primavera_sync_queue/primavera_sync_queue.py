# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta


class PrimaveraSyncQueue(Document):
	def before_insert(self):
		"""Set queue timestamp before insert"""
		if not self.queue_timestamp:
			self.queue_timestamp = datetime.now()
		
		# Set next attempt if not set
		if not self.next_attempt:
			self.next_attempt = datetime.now()
	
	def autoname(self):
		"""Generate name from naming series"""
		if not self.naming_series:
			self.naming_series = "P6-QUEUE-.YYYY.-.MM.-.#####"
		super().autoname()
	
	def process_sync(self):
		"""Process the sync operation"""
		from omnexa_construction.integrations.primavera_p6 import get_p6_client, PrimaveraP6Sync
		
		try:
			# Update status to In Progress
			self.status = "In Progress"
			self.last_attempt = datetime.now()
			self.save()
			
			# Get P6 client and sync manager
			p6_client = get_p6_client()
			sync_manager = PrimaveraP6Sync(p6_client)
			
			# Process based on entity type and direction
			result = None
			if self.sync_direction in ["To P6", "Bi-directional"]:
				if self.entity_type == "Project":
					result = sync_manager.sync_project_to_p6(self.entity_id)
				elif self.entity_type == "Task":
					result = sync_manager.sync_task_to_p6(self.entity_id)
				elif self.entity_type == "Resource":
					result = sync_manager.sync_resource_to_p6(self.entity_id)
			
			if self.sync_direction in ["From P6", "Bi-directional"]:
				if self.entity_type == "Project":
					result = sync_manager.sync_project_from_p6(self.entity_id)
			
			# Update status based on result
			if result and result.get('status') == 'success':
				self.status = "Completed"
				self.error_message = None
			else:
				self.status = "Failed"
				self.error_message = result.get('error') if result else "Unknown error"
				
				# Increment retry count
				self.retry_count += 1
				
				# Schedule retry if under max retries
				if self.retry_count < self.max_retries:
					self.status = "Pending"
					# Exponential backoff
					backoff_minutes = 2 ** self.retry_count
					self.next_attempt = datetime.now() + timedelta(minutes=backoff_minutes)
			
			self.save()
			return result
			
		except Exception as e:
			self.status = "Failed"
			self.error_message = str(e)
			self.retry_count += 1
			
			if self.retry_count < self.max_retries:
				self.status = "Pending"
				backoff_minutes = 2 ** self.retry_count
				self.next_attempt = datetime.now() + timedelta(minutes=backoff_minutes)
			
			self.save()
			frappe.log_error(f"Sync queue processing failed: {str(e)}", "Primavera Sync Queue")
			return {'status': 'failed', 'error': str(e)}
