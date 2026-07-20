# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe


def execute():
	"""Before dropping `project` from BOQ Item, copy values into project_contract when missing."""
	if not frappe.db.has_column("BOQ Item", "project"):
		return
	if not frappe.db.has_column("BOQ Item", "project_contract"):
		return
	frappe.db.sql(
		"""
		UPDATE `tabBOQ Item`
		SET `project_contract` = `project`
		WHERE IFNULL(`project_contract`, '') = '' AND IFNULL(`project`, '') != ''
		"""
	)
