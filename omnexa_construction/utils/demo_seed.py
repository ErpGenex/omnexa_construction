from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, add_months, cint, flt, getdate, today

DEMO_MARKER = "DEMO-CONST-"

PROJECT_SPECS: list[dict] = [
	{
		"code": "01",
		"title_en": "Highway Expansion — Cairo–Alexandria",
		"title_ar": "توسعة طريق القاهرة–الإسكندرية",
		"contract_value": 45_000_000,
		"contract_type": "Unit Price",
		"segment": "Infrastructure",
		"governing": "FIDIC 2017 Red Book (Building & Engineering)",
		"site": "Km 42–68, Desert Road",
	},
	{
		"code": "02",
		"title_en": "Residential Tower — New Capital",
		"title_ar": "برج سكني — العاصمة الإدارية",
		"contract_value": 120_000_000,
		"contract_type": "Lump Sum",
		"segment": "Buildings",
		"governing": "FIDIC 2017 Red Book (Building & Engineering)",
		"site": "District R7, Plot 12",
	},
	{
		"code": "03",
		"title_en": "Hospital EPC — Giza",
		"title_ar": "مستشفى تسليم مفتاح — الجيزة",
		"contract_value": 85_000_000,
		"contract_type": "Turnkey (EPC)",
		"segment": "Buildings",
		"governing": "FIDIC 2017 Silver Book (EPC/Turnkey)",
		"site": "6th of October, Zone B",
	},
	{
		"code": "04",
		"title_en": "Industrial Plant — 10th of Ramadan",
		"title_ar": "مصنع صناعي — العاشر من رمضان",
		"contract_value": 62_000_000,
		"contract_type": "Cost Plus",
		"segment": "Industrial EPC",
		"governing": "FIDIC 2017 Yellow Book (M&E Design-Build)",
		"site": "B10 Industrial Zone",
	},
	{
		"code": "05",
		"title_en": "Utilities & Roads — New City",
		"title_ar": "مرافق وطرق — مدينة جديدة",
		"contract_value": 38_000_000,
		"contract_type": "Unit Price",
		"segment": "Infrastructure",
		"governing": "FIDIC 2017 Red Book (Building & Engineering)",
		"site": "Phase 2 network",
	},
]

# (description, cost_code, quantity, unit_cost, lump_total) — lump_total>0 overrides unit pricing
BOQ_LINE_TEMPLATES = [
	("Earthworks & excavation", "01.10", 1200, 450, 0),
	("Concrete structure", "03.20", 850, 1200, 0),
	("MEP installation", "15.00", 1, 0, 2_500_000),
	("Finishes & cladding", "09.40", 3200, 680, 0),
	("External works", "31.00", 1, 0, 1_800_000),
]

IPC_PROGRESS_STEPS = (20.0, 45.0, 70.0)


def _assert_admin() -> None:
	if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
		return
	if "System Manager" not in (frappe.get_roles() or []):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _resolve_branch(company: str, branch: str | None) -> str:
	if branch and frappe.db.exists("Branch", {"name": branch, "company": company}):
		return branch
	found = frappe.db.get_value("Branch", {"company": company}, "name", order_by="creation asc")
	if not found:
		frappe.throw(_("No branch found for company {0}. Create a branch first.").format(company))
	return found


def _company_currency(company: str) -> str:
	return frappe.db.get_value("Company", company, "default_currency") or "EGP"


def _gl_defaults(company: str) -> tuple[str | None, str | None]:
	row = frappe.db.get_value(
		"Company",
		company,
		["default_opex_gl", "default_trade_payable_gl", "default_cogs_gl"],
		as_dict=True,
	)
	expense = row.default_opex_gl or row.default_cogs_gl
	payable = row.default_trade_payable_gl
	return expense, payable


def _ensure_customer(company: str, name: str, display: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": name, "company": company}, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": "Customer", "customer_name": name, "company": company})
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_supplier(company: str, name: str) -> str:
	existing = frappe.db.get_value("Supplier", {"supplier_name": name, "company": company}, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": "Supplier", "supplier_name": name, "company": company})
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_demo_item(company: str) -> str | None:
	if not frappe.db.exists("DocType", "Item"):
		return None
	code = f"{DEMO_MARKER}MAT-{company}"
	existing = frappe.db.get_value("Item", {"item_code": code, "company": company}, "name")
	if existing:
		return existing
	if not frappe.db.exists("UOM", "Nos"):
		frappe.get_doc({"doctype": "UOM", "uom_name": "Nos"}).insert(ignore_permissions=True)
	item = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": code,
			"item_name": "Construction demo — site materials",
			"company": company,
			"stock_uom": "Nos",
			"is_stock_item": 1,
		}
	)
	item.insert(ignore_permissions=True)
	return item.name


def _contract_title(spec: dict) -> str:
	return f"{DEMO_MARKER}{spec['code']} {spec['title_en']}"


def _already_seeded(company: str) -> bool:
	title = _contract_title(PROJECT_SPECS[0])
	return bool(frappe.db.exists("Project Contract", {"company": company, "contract_title": title}))


def seed_construction_portfolio_demo(
	company: str,
	branch: str | None = None,
	force: int | str | None = 0,
) -> dict:
	"""Seed five construction projects with owners, subcontractors, BOQ, IPC, SPC, site, WIP, and optional stock."""
	_assert_admin()
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found").format(company))

	branch = _resolve_branch(company, branch)
	currency = _company_currency(company)
	expense_gl, payable_gl = _gl_defaults(company)

	if _already_seeded(company) and not cint(force):
		return {
			"ok": True,
			"skipped": True,
			"message": _("Construction demo data already exists. Use force=1 to add another portfolio (not recommended)."),
			"contracts": frappe.get_all(
				"Project Contract",
				filters={"company": company, "contract_title": ["like", f"{DEMO_MARKER}%"]},
				pluck="name",
			),
		}

	summary: dict = {
		"ok": True,
		"skipped": False,
		"company": company,
		"branch": branch,
		"customers": [],
		"suppliers": [],
		"contracts": [],
		"boq_items": 0,
		"ipc_certificates": 0,
		"subcontract_work_orders": 0,
		"subcontract_payment_certificates": 0,
		"site_daily_reports": 0,
		"change_orders": 0,
		"wip_snapshots": 0,
		"purchase_orders": 0,
		"gl_posted_spc": 0,
	}

	owners: list[str] = []
	subs: list[str] = []
	for i in range(1, 6):
		owners.append(
			_ensure_customer(
				company,
				f"{DEMO_MARKER}OWNER-{i:02d}",
				f"Owner {i} — {PROJECT_SPECS[i - 1]['title_en'][:40]}",
			)
		)
	for i in range(1, 4):
		subs.append(_ensure_supplier(company, f"{DEMO_MARKER}SUB-{i:02d}"))
	summary["customers"] = owners
	summary["suppliers"] = subs

	demo_item = _ensure_demo_item(company)
	base_date = getdate(today())

	for idx, spec in enumerate(PROJECT_SPECS):
		owner = owners[idx]
		sub = subs[idx % len(subs)]
		title = _contract_title(spec)
		start = add_months(base_date, -6 + idx)
		end = add_months(start, 18)

		contract = frappe.get_doc(
			{
				"doctype": "Project Contract",
				"contract_title": title,
				"contract_type": spec["contract_type"],
				"client": owner,
				"letter_of_acceptance_date": start,
				"contract_currency": currency,
				"retention_percent": 5,
				"advance_payment": flt(spec["contract_value"]) * 0.1,
				"payment_terms": "Monthly IPC — net 30 days",
				"governing_standard": spec.get("governing") or "FIDIC 2017 Red Book (Building & Engineering)",
				"project_segment": spec["segment"],
				"planned_start": start,
				"planned_completion": end,
				"site_location": spec["site"],
				"contract_value": spec["contract_value"],
				"status": "Active",
				"company": company,
				"branch": branch,
			}
		)
		contract.insert(ignore_permissions=True)
		if contract.meta.is_submittable:
			contract.submit()
		summary["contracts"].append(contract.name)

		boq_names: list[str] = []
		for line_idx, (desc, cost_code, qty, unit_cost, lump) in enumerate(BOQ_LINE_TEMPLATES):
			if lump:
				uc = flt(lump) / max(flt(qty), 1)
				ac = flt(lump) * (0.35 + 0.1 * line_idx)
			else:
				uc = unit_cost
				ac = flt(qty) * flt(unit_cost) * (0.4 + 0.08 * line_idx)
			boq = frappe.get_doc(
				{
					"doctype": "BOQ Item",
					"project_contract": contract.name,
					"section_name": f"Section {line_idx + 1}",
					"cost_code": cost_code,
					"item_description": desc,
					"quantity": qty,
					"unit_of_measure": "m³" if line_idx == 0 else "Nos",
					"unit_cost": uc,
					"actual_cost": ac,
					"completion_percent": min(75, 15 * (line_idx + 1) + idx * 3),
					"company": company,
					"branch": branch,
				}
			)
			boq.insert(ignore_permissions=True)
			boq_names.append(boq.name)
			summary["boq_items"] += 1

		scw = frappe.get_doc(
			{
				"doctype": "Subcontract Work Order",
				"project_contract": contract.name,
				"subcontractor": sub,
				"scope_of_work": f"Subcontract package — {spec['title_en']}",
				"contract_value": flt(spec["contract_value"]) * 0.35,
				"progress_percent": IPC_PROGRESS_STEPS[-1],
				"status": "Active",
				"company": company,
				"branch": branch,
			}
		)
		scw.insert(ignore_permissions=True)
		summary["subcontract_work_orders"] += 1

		for step_i, pct in enumerate(IPC_PROGRESS_STEPS):
			ipc_date = add_days(add_months(start, step_i + 2), 5)
			ipc = frappe.get_doc(
				{
					"doctype": "IPC Certificate",
					"project_contract": contract.name,
					"ipc_date": ipc_date,
					"period_from": add_days(ipc_date, -30),
					"period_to": ipc_date,
					"employer_certificate_ref": f"ENG/IPC/{spec['code']}/{step_i + 1}",
					"boq_completion_percent": pct,
					"status": "Certified",
					"company": company,
					"branch": branch,
					"certificate_reference": f"{DEMO_MARKER}IPC-{spec['code']}-{step_i + 1}",
				}
			)
			ipc.insert(ignore_permissions=True)
			summary["ipc_certificates"] += 1

		if expense_gl and payable_gl:
			for cert_i, fraction in enumerate((0.25, 0.55)):
				cert_date = add_days(add_months(start, 3 + cert_i), 10)
				certified = flt(scw.contract_value) * fraction
				spc = frappe.get_doc(
					{
						"doctype": "Subcontract Payment Certificate",
						"subcontract_work_order": scw.name,
						"certificate_date": cert_date,
						"certified_amount": certified,
						"previously_paid": certified * fraction * 0.5 if cert_i else 0,
						"retention_percent": 5,
						"status": "Draft",
						"expense_account": expense_gl,
						"payable_account": payable_gl,
						"company": company,
						"branch": branch,
						"payment_reference": f"{DEMO_MARKER}SPC-{spec['code']}-{cert_i + 1}",
					}
				)
				spc.insert(ignore_permissions=True)
				if spc.meta.is_submittable:
					try:
						spc.submit()
						summary["gl_posted_spc"] += 1
					except Exception:
						frappe.log_error(
							frappe.get_traceback(),
							f"Construction demo: SPC submit failed for {spc.name}",
						)
				summary["subcontract_payment_certificates"] += 1

		for day_offset in (7, 21):
			sdr = frappe.get_doc(
				{
					"doctype": "Site Daily Report",
					"project": contract.name,
					"report_date": add_days(base_date, -day_offset - idx),
					"boq_item": boq_names[0] if boq_names else None,
					"weather": "Clear / 28°C",
					"work_summary": f"Progress on {spec['title_en']} — pour, steel fix, QA hold points.",
					"labor_count": 45 + idx * 8,
					"equipment_hours": 32 + idx * 4,
					"material_consumed_cost": 125_000 + idx * 15_000,
					"company": company,
					"branch": branch,
					"report_reference": f"{DEMO_MARKER}SDR-{spec['code']}-{day_offset}",
				}
			)
			sdr.insert(ignore_permissions=True)
			summary["site_daily_reports"] += 1

		if idx in (0, 2, 4):
			co = frappe.get_doc(
				{
					"doctype": "Construction Change Order",
					"project_contract": contract.name,
					"order_date": add_days(start, 45),
					"title": f"VO-{spec['code']} — scope adjustment",
					"contract_clause_reference": "Sub-Clause 13.3",
					"description": "Employer variation — additional MEP scope and revised programme.",
					"cost_impact": flt(spec["contract_value"]) * 0.03,
					"time_impact_days": 14,
					"status": "Approved",
					"company": company,
					"branch": branch,
				}
			)
			co.insert(ignore_permissions=True)
			summary["change_orders"] += 1

		last_ipc = frappe.db.get_value(
			"IPC Certificate",
			{"project_contract": contract.name, "status": "Certified"},
			"net_amount",
			order_by="ipc_date desc",
		)
		wip = frappe.get_doc(
			{
				"doctype": "Project WIP Snapshot",
				"project_contract": contract.name,
				"snapshot_date": base_date,
				"cost_to_date": flt(spec["contract_value"]) * 0.42,
				"revenue_recognized": flt(last_ipc or 0) * 0.85,
				"company": company,
				"branch": branch,
				"snapshot_reference": f"{DEMO_MARKER}WIP-{spec['code']}",
			}
		)
		wip.insert(ignore_permissions=True)
		summary["wip_snapshots"] += 1

		if demo_item and frappe.db.exists("DocType", "Purchase Order"):
			try:
				po = frappe.get_doc(
					{
						"doctype": "Purchase Order",
						"company": company,
						"branch": branch,
						"supplier": sub,
						"posting_date": add_days(base_date, -14 - idx),
						"items": [
							{
								"item": demo_item,
								"item_code": demo_item,
								"qty": 50 + idx * 10,
								"rate": 1200 + idx * 100,
							}
						],
					}
				)
				po.insert(ignore_permissions=True)
				if po.meta.is_submittable and po.docstatus == 0:
					po.submit()
				summary["purchase_orders"] += 1
			except Exception:
				frappe.log_error(
					frappe.get_traceback(),
					f"Construction demo: PO failed for contract {contract.name}",
				)

	frappe.db.commit()
	summary["message"] = _(
		"Created {0} project contracts with BOQ, IPC, subcontractors, site reports, and WIP."
	).format(len(summary["contracts"]))
	return summary
