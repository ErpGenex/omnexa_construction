from frappe.model.document import Document

from omnexa_construction.construction_forms.helpers import hydrate_contract_party_fields


class ConstructionMaterialApprovalRequest(Document):
	def validate(self):
		hydrate_contract_party_fields(self)
