import frappe
from frappe.utils import flt


def post_gl_journal(*, company: str, branch: str | None, posting_date, reference: str, remarks: str, lines: list[dict]) -> str:
	je = frappe.new_doc("Journal Entry")
	je.company = company
	je.branch = branch
	je.posting_date = posting_date
	je.reference = reference
	je.remarks = remarks
	for row in lines:
		je.append(
			"accounts",
			{
				"account": row["account"],
				"debit": flt(row.get("debit") or 0),
				"credit": flt(row.get("credit") or 0),
			},
		)
	je.insert()
	je.submit()
	return je.name

