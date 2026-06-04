# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PrimaveraP6Settings(Document):
	def validate(self):
		"""Validate settings"""
		if self.enabled:
			if not all([self.base_url, self.username, self.password, self.company_id]):
				frappe.throw(_("All connection fields are required when integration is enabled"))
	
	def test_connection(self):
		"""Test connection to Primavera P6"""
		try:
			from omnexa_construction.integrations.primavera_p6 import PrimaveraP6Client
			
			client = PrimaveraP6Client(
				base_url=self.base_url,
				username=self.username,
				password=self.get_password('password'),
				company_id=self.company_id
			)
			
			# Try to get projects as a test
			projects = client.get_projects()
			
			frappe.msgprint(_("Connection successful! Found {0} projects in P6").format(len(projects)))
			return True
			
		except Exception as e:
			frappe.throw(_("Connection failed: {0}").format(str(e)))
