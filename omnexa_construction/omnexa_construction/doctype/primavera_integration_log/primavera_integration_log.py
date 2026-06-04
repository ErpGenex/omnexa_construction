# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime


class PrimaveraIntegrationLog(Document):
	def before_insert(self):
		"""Set sync timestamp before insert"""
		if not self.sync_timestamp:
			self.sync_timestamp = datetime.now()
	
	def autoname(self):
		"""Generate name from naming series"""
		if not self.naming_series:
			self.naming_series = "P6-LOG-.YYYY.-.MM.-.#####"
		super().autoname()
