from __future__ import annotations

import frappe
from frappe.model.document import Document

from omnexa_construction.construction_forms.helpers import hydrate_contract_party_fields


class ConstructionWorkApprovalRequest(Document):
	def validate(self):
		hydrate_contract_party_fields(self)
