# Copyright (c) 2026, Omnexa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class Uniclass2015Classification(Document):
	def autoname(self):
		"""Generate name from naming series"""
		if not self.naming_series:
			self.naming_series = "UNI-.####"
		super().autoname()
	
	def validate(self):
		"""Validate classification code format"""
		if self.code:
			# Uniclass 2015 code format: Co_XX_XX_XX
			if not self.code.startswith('Co_'):
				frappe.throw(_('Uniclass 2015 code must start with "Co_"'))
