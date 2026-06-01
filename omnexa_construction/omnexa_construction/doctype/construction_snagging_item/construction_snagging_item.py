import frappe
from frappe.model.document import Document


class ConstructionSnaggingItem(Document):
	def validate(self):
		if self.status == "Closed" and not self.actual_close_date:
			self.actual_close_date = frappe.utils.today()
		self._sync_dlp_open_count()

	def on_update(self):
		self._sync_dlp_open_count()

	def _sync_dlp_open_count(self):
		if not self.dlp_record or not frappe.db.exists("DocType", "Construction DLP Record"):
			return
		open_count = frappe.db.count(
			"Construction Snagging Item",
			{"dlp_record": self.dlp_record, "status": ["!=", "Closed"], "docstatus": ["<", 2]},
		)
		if frappe.get_meta("Construction DLP Record").has_field("open_defects_count"):
			frappe.db.set_value("Construction DLP Record", self.dlp_record, "open_defects_count", open_count)
