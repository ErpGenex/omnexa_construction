# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from __future__ import annotations

import frappe


def execute():
	frappe.reload_doc("omnexa_construction", "doctype", "project_contract_term")
	frappe.reload_doc("omnexa_construction", "doctype", "project_contract")
