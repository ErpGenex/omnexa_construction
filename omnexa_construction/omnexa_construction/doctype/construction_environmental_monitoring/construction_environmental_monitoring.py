import frappe
from frappe.model.document import Document


class ConstructionEnvironmentalMonitoring(Document):
	def validate(self):
		if self.limit_value and self.measurement_value and self.measurement_value > self.limit_value:
			self.compliance_status = "Non-Compliant"
