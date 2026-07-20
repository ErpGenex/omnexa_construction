# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""SAP PS / Oracle Unifier export connectors (MVP payloads)."""

from __future__ import annotations

import json

import frappe
from frappe import _


@frappe.whitelist()
def export_wbs_to_sap_ps(project_contract: str) -> dict:
	contract = frappe.get_doc("Project Contract", project_contract)
	boq = frappe.get_all(
		"BOQ Item",
		filters={"project_contract": project_contract, "docstatus": ["<", 2]},
		fields=["name", "description", "cost_code", "qty", "rate", "amount"],
		limit=10000,
	)
	payload = {
		"system": "SAP_PS",
		"project_definition": contract.name,
		"company_code": contract.company,
		"wbs_elements": [
			{
				"wbs_id": row.cost_code or row.name,
				"description": row.description,
				"planned_cost": row.amount,
				"quantity": row.qty,
			}
			for row in boq
		],
	}
	return {"ok": True, "count": len(boq), "payload": payload, "json": json.dumps(payload, indent=2)}


@frappe.whitelist()
def export_cost_to_oracle_unifier(project_contract: str) -> dict:
	from omnexa_construction.evm_metrics import evm_snapshot

	snap = evm_snapshot(project_contract)
	payload = {
		"system": "Oracle_Unifier",
		"project_number": project_contract,
		"bac": snap.get("bac"),
		"ev": snap.get("ev"),
		"ac": snap.get("ac"),
		"eac": snap.get("eac"),
		"spi": snap.get("spi"),
		"cpi": snap.get("cpi"),
	}
	return {"ok": True, "payload": payload, "json": json.dumps(payload, indent=2)}
