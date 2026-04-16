import frappe
from frappe.model.document import Document
from frappe.utils import flt, today
from omnexa_construction.utils.gl import post_gl_journal


class SubcontractPaymentCertificate(Document):
	def validate(self):
		self._hydrate_from_subcontract()
		self.retention_amount = flt(self.certified_amount) * (flt(self.retention_percent) / 100.0)
		self.net_payable = flt(self.certified_amount) - flt(self.previously_paid) - flt(self.retention_amount)

	def on_submit(self):
		self._post_accrual_journal()
		self.db_set("status", "Approved", update_modified=False)

	def on_cancel(self):
		self._reverse_journal()
		self.db_set("status", "Draft", update_modified=False)

	def on_update_after_submit(self):
		if self.status == "Paid" and not self.payment_entry:
			self._create_payment_entry()
		if self.status == "Retention Released" and not self.retention_payment_entry:
			self._create_retention_payment_entry()

	def _hydrate_from_subcontract(self):
		if not self.subcontract_work_order:
			return
		row = frappe.db.get_value(
			"Subcontract Work Order",
			self.subcontract_work_order,
			["project_contract", "subcontractor", "company", "branch"],
			as_dict=True,
		)
		if not row:
			return
		self.project_contract = row.project_contract
		self.subcontractor = row.subcontractor
		self.company = self.company or row.company
		self.branch = self.branch or row.branch
		if self.is_new() and row.project_contract:
			cr = frappe.db.get_value("Project Contract", row.project_contract, "retention_percent")
			if cr is not None:
				self.retention_percent = flt(cr)

	def _post_accrual_journal(self):
		if flt(self.net_payable) <= 0:
			return
		if not (self.expense_account and self.payable_account):
			frappe.throw("Set expense_account and payable_account before submit.")
		je = post_gl_journal(
			company=self.company,
			branch=self.branch,
			posting_date=self.certificate_date,
			reference=self.name,
			remarks=f"Subcontract payment accrual {self.name}",
			lines=[
				{"account": self.expense_account, "debit": self.net_payable, "credit": 0},
				{"account": self.payable_account, "debit": 0, "credit": self.net_payable},
			],
		)
		self.db_set("journal_entry", je, update_modified=False)

	def _reverse_journal(self):
		if self.journal_entry and frappe.db.exists("Journal Entry", self.journal_entry):
			je = frappe.get_doc("Journal Entry", self.journal_entry)
			if je.docstatus == 1:
				je.cancel()

	def _create_payment_entry(self):
		if flt(self.net_payable) <= 0:
			return
		pe = frappe.new_doc("Payment Entry")
		pe.company = self.company
		pe.branch = self.branch
		pe.party_type = "Supplier"
		pe.party = self.subcontractor
		pe.posting_date = self.payment_date or today()
		pe.paid_amount = self.net_payable
		pe.mode_of_payment = self.mode_of_payment
		pe.bank_account = self.bank_account
		pe.insert(ignore_permissions=True)
		pe.submit()
		self.db_set("payment_entry", pe.name, update_modified=False)

	def _create_retention_payment_entry(self):
		if flt(self.retention_amount) <= 0:
			return
		pe = frappe.new_doc("Payment Entry")
		pe.company = self.company
		pe.branch = self.branch
		pe.party_type = "Supplier"
		pe.party = self.subcontractor
		pe.posting_date = self.retention_release_date or today()
		pe.paid_amount = self.retention_amount
		pe.mode_of_payment = self.retention_mode_of_payment
		pe.bank_account = self.retention_bank_account
		pe.insert(ignore_permissions=True)
		pe.submit()
		self.db_set("retention_payment_entry", pe.name, update_modified=False)


@frappe.whitelist()
def release_retention(name: str, retention_release_date: str | None = None, retention_mode_of_payment: str | None = None, retention_bank_account: str | None = None):
	if not _can_release_retention(frappe.session.user):
		frappe.throw("You are not allowed to release retention.")
	doc = frappe.get_doc("Subcontract Payment Certificate", name)
	if doc.docstatus != 1:
		frappe.throw("Only submitted certificates can release retention.")
	if doc.status != "Paid":
		frappe.throw("Retention can be released only after certificate is marked Paid.")
	if doc.status == "Retention Released":
		return {"name": doc.name, "status": doc.status, "retention_payment_entry": doc.retention_payment_entry}
	doc.retention_release_date = retention_release_date or today()
	doc.retention_mode_of_payment = retention_mode_of_payment
	doc.retention_bank_account = retention_bank_account
	doc.status = "Retention Released"
	doc.save(ignore_permissions=True)
	return {"name": doc.name, "status": doc.status, "retention_payment_entry": doc.retention_payment_entry}


def _can_release_retention(user: str) -> bool:
	allowed_roles = {"System Manager", "Accounts Manager", "Project Manager"}
	user_roles = set(frappe.get_roles(user))
	return bool(allowed_roles.intersection(user_roles))

