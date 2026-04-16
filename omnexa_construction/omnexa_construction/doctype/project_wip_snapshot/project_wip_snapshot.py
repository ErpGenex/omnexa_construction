from frappe.model.document import Document
from frappe.utils import flt


class ProjectWIPSnapshot(Document):
	def validate(self):
		self.wip_balance = flt(self.cost_to_date) - flt(self.revenue_recognized)

