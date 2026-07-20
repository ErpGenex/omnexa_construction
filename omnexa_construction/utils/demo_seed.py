from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, add_months, cint, flt, getdate, now_datetime, today

DEMO_MARKER = "DEMO-CONST-"
PROJECT_COUNT = 20

_BASE_PROJECT_SPECS: list[dict] = [
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
		"site": "B10 Industrial Zone"
	},
	{
		"code": "05",
		"title_en": "Utilities & Roads — New City",
		"title_ar": "مرافق وطرق — مدينة جديدة",
		"contract_value": 38_000_000,
		"contract_type": "Unit Price",
		"segment": "Infrastructure",
		"governing": "FIDIC 2017 Red Book (Building & Engineering)",
		"site": "Phase 2 network"
	},
]

_EXTRA_PROJECT_SPECS: list[dict] = [
	{"code": "06", "title_en": "Metro Station — Line 3 Extension", "title_ar": "محطة مترو — امتداد الخط 3", "contract_value": 95_000_000, "contract_type": "Lump Sum", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Attaba interchange"
	},
	{"code": "07", "title_en": "Nile Bridge — East Bank Link", "title_ar": "كوبري النيل — الضفة الشرقية", "contract_value": 78_000_000, "contract_type": "Unit Price", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Rod El Farag corridor"
	},
	{"code": "08", "title_en": "Water Treatment Plant — 6th October", "title_ar": "محطة معالجة مياه — 6 أكتوبر", "contract_value": 54_000_000, "contract_type": "Turnkey (EPC)", "segment": "Infrastructure", "governing": "FIDIC 2017 Silver Book (EPC/Turnkey)", "site": "WWTP Zone C"
	},
	{"code": "09", "title_en": "132 kV Substation EPC", "title_ar": "محطة كهرباء 132 ك.ف", "contract_value": 41_000_000, "contract_type": "Turnkey (EPC)", "segment": "Industrial EPC", "governing": "FIDIC 2017 Yellow Book (M&E Design-Build)", "site": "Badr City grid node"
	},
	{"code": "10", "title_en": "Commercial Mall — Sheikh Zayed", "title_ar": "مول تجاري — الشيخ زايد", "contract_value": 110_000_000, "contract_type": "Lump Sum", "segment": "Buildings", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Plot 44, Arkan"},
	{"code": "11", "title_en": "Data Center — Smart Village", "title_ar": "مركز بيانات — Smart Village", "contract_value": 67_000_000, "contract_type": "Turnkey (EPC)", "segment": "Industrial EPC", "governing": "FIDIC 2017 Silver Book (EPC/Turnkey)", "site": "Tier III hall build-out"
	},
	{"code": "12", "title_en": "Airport Taxiway Rehabilitation", "title_ar": "تأهيل مدارج مطار", "contract_value": 52_000_000, "contract_type": "Unit Price", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Cairo International — TWY B"
	},
	{"code": "13", "title_en": "Social Housing — 3,000 Units", "title_ar": "إسكان اجتماعي — 3000 وحدة", "contract_value": 145_000_000, "contract_type": "Unit Price", "segment": "Buildings", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "New Damietta phases 1–3"
	},
	{"code": "14", "title_en": "Refinery Turnaround Package", "title_ar": "حزمة إيقاف تشغيل مصفاة", "contract_value": 88_000_000, "contract_type": "Cost Plus", "segment": "Industrial EPC", "governing": "FIDIC 2017 Yellow Book (M&E Design-Build)", "site": "Mostorod refinery"
	},
	{"code": "15", "title_en": "Solar Farm 50 MW", "title_ar": "محطة طاقة شمسية 50 م.و", "contract_value": 73_000_000, "contract_type": "Lump Sum", "segment": "Industrial EPC", "governing": "FIDIC 2017 Silver Book (EPC/Turnkey)", "site": "Benban sector 4"
	},
	{"code": "16", "title_en": "Port Berth Extension — East Port Said", "title_ar": "توسعة رصيف ميناء — بورسعيد", "contract_value": 98_000_000, "contract_type": "Unit Price", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Berth 7 quay wall"
	},
	{"code": "17", "title_en": "University Campus Phase 2", "title_ar": "حرم جامعي — المرحلة 2", "contract_value": 56_000_000, "contract_type": "Lump Sum", "segment": "Buildings", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "New Cairo academic zone"
	},
	{"code": "18", "title_en": "Hotel & Convention Center", "title_ar": "فندق ومركز مؤتمرات", "contract_value": 132_000_000, "contract_type": "Turnkey (EPC)", "segment": "Buildings", "governing": "FIDIC 2017 Silver Book (EPC/Turnkey)", "site": "North Coast KM 98"
	},
	{"code": "19", "title_en": "Railway Electrification Lot 2", "title_ar": "كهربة السكك الحديدية — Lot 2", "contract_value": 64_000_000, "contract_type": "Unit Price", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "Beni Suef–Asyut corridor"
	},
	{"code": "20", "title_en": "Wastewater Network Phase 3", "title_ar": "شبكة صرف — المرحلة 3", "contract_value": 47_000_000, "contract_type": "Unit Price", "segment": "Infrastructure", "governing": "FIDIC 2017 Red Book (Building & Engineering)", "site": "New Administrative Capital utilities"
	},
]

PROJECT_SPECS: list[dict] = (_BASE_PROJECT_SPECS + _EXTRA_PROJECT_SPECS)[:PROJECT_COUNT]

BOQ_LINE_TEMPLATES = [
	("Earthworks & excavation", "01.10", 1200, 450, 0),
	("Concrete structure", "03.20", 850, 1200, 0),
	("Structural steel supply & erect", "05.10", 420, 2800, 0),
	("MEP installation", "15.00", 1, 0, 2_500_000),
	("Finishes & cladding", "09.40", 3200, 680, 0),
	("External works & landscaping", "31.00", 1, 0, 1_800_000),
]

# suffix, English name, Arabic name, UOM, product_type, classification
CONSTRUCTION_MATERIAL_CATALOG: list[tuple[str, str, str, str, str, str]] = [
	("MAT-CEM-OPC", "Portland Cement (OPC 42.5N)", "أسمنت بورتلاند (OPC 42.5N)", "Bag", "Raw Material", "CEM"),
	("MAT-CEM-WHITE", "White Cement", "أسمنت أبيض", "Bag", "Raw Material", "CEM"),
	("MAT-SAND-FINE", "Fine Sand (Washed)", "رمل ناعم (مغسول)", "m³", "Raw Material", "AGG"),
	("MAT-SAND-COARSE", "Coarse Sand", "رمل خشن", "m³", "Raw Material", "AGG"),
	("MAT-GRAVEL", "Crushed Gravel 20mm", "حصى مكسر 20 مم", "m³", "Raw Material", "AGG"),
	("MAT-BASE", "Sub-base / Road Base", "طبقة أساس / تأسيس طرق", "m³", "Raw Material", "AGG"),
	("MAT-STEEL-R12", "Reinforcement Steel Ø12mm", "حديد تسليح 12 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R16", "Reinforcement Steel Ø16mm", "حديد تسليح 16 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R25", "Reinforcement Steel Ø25mm", "حديد تسليح 25 مم", "Ton", "Raw Material", "STL"),
	("MAT-MESH", "Welded Wire Mesh", "شبك حديد ملحوم", "m²", "Raw Material", "STL"),
	("MAT-STRUCT-STL", "Structural Steel Sections", "Profiles فولاذ إنشائي", "Ton", "Raw Material", "STL"),
	("MAT-RMX-C30", "Ready-Mix Concrete C30/37", "خرسانة جاهزة C30/37", "m³", "Raw Material", "CON"),
	("MAT-RMX-C40", "Ready-Mix Concrete C40/50", "خرسانة جاهزة C40/50", "m³", "Raw Material", "CON"),
	("MAT-BLOCK", "Concrete Hollow Block", "بلك خرساني مفرغ", "Nos", "Raw Material", "MAS"),
	("MAT-BRICK", "Red Clay Brick", "طوب أحمر", "Nos", "Raw Material", "MAS"),
	("MAT-TIMBER", "Formwork Timber / Ply", "خشب قوالب / أبلكاش", "m³", "Raw Material", "FRM"),
	("MAT-WATERPROOF", "Bituminous Waterproof Membrane", "غشاء عزل bituminous", "Roll", "Raw Material", "INS"),
	("MAT-INS-FOAM", "Thermal Insulation Foam Board", "لوح عزل حراري", "m²", "Raw Material", "INS"),
	("MAT-PVC-PIPE", "PVC Pressure Pipe 110mm", "مواسير PVC ضغط 110 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PPR-PIPE", "PPR Hot Water Pipe", "مواسير PPR للمياه الساخنة", "Meter", "Raw Material", "MEP"),
	("MAT-COPPER", "Copper Pipe 22mm", "مواسير نحاس 22 مم", "Meter", "Raw Material", "MEP"),
	("MAT-CABLE-LV", "LV Power Cable 4×16mm²", "كابل طاقة منخفض 4×16 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-MV", "MV Power Cable", "كابل طاقة متوسط", "Meter", "Raw Material", "ELE"),
	("MAT-PAINT-EXT", "External Acrylic Paint", "دهان أكريليك خارجي", "Liter", "Consumable", "FIN"),
	("MAT-PAINT-INT", "Internal Emulsion Paint", "دهان داخلي", "Liter", "Consumable", "FIN"),
	("MAT-TILE-FLR", "Porcelain Floor Tile 60×60", "سيراميك أرضيات 60×60", "m²", "Raw Material", "FIN"),
	("MAT-GLASS", "Tempered Glass 10mm", "زجاج مقسى 10 مم", "m²", "Raw Material", "FIN"),
	("MAT-ALUM", "Aluminum Curtain Wall Profile", "Profile ألوميتال كرتن وول", "Meter", "Raw Material", "FIN"),
	("MAT-ASPHALT", "Hot Mix Asphalt (HMA)", "أسفلت ساخن", "Ton", "Raw Material", "RDW"),
	("MAT-GEOTEXT", "Geotextile Separation Layer", "Geotextile فصل", "m²", "Raw Material", "RDW"),
	("MAT-ADMX", "Concrete Plasticizer Admixture", "مادة ملونة للخرسانة", "Liter", "Consumable", "CEM"),
	("MAT-GYPSUM", "Gypsum Board 12.5mm", "جبس بورد 12.5 مم", "m²", "Raw Material", "FIN"),
	("MAT-DUCT", "Galvanized HVAC Duct", "مجاري تكييف مجلفنة", "Kg", "Raw Material", "MEP"),
	("MAT-FIRE-SEAL", "Fire Stop Sealant", "مادة مانعة للحريق", "Nos", "Consumable", "SAF"),
	("MAT-DIESEL", "Diesel Fuel (Site)", "سولار موقع", "Liter", "Consumable", "FUEL"),
	("MAT-LUBRIC", "Heavy Equipment Lubricant", "زيت تشحيم معدات", "Liter", "Consumable", "FUEL"),
]

IPC_PROGRESS_STEPS = (15.0, 35.0, 55.0, 75.0)
SITE_REPORT_OFFSETS = (7, 21, 35, 49)


def _assert_admin() -> None:
	if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
		return
	if "System Manager" not in (frappe.get_roles() or []):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _resolve_branch(company: str, branch: str | None) -> str:
	if branch and frappe.db.exists("Branch", {"name": branch, "company": company
	}):
		return branch
	found = frappe.db.get_value("Branch", {"company": company
	}, "name", order_by="creation asc")
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


def _contract_status(idx: int) -> str:
	if idx >= PROJECT_COUNT - 2:
		return "Closed"
	if idx >= PROJECT_COUNT - 4:
		return "Suspended"
	return "Active"


def _ensure_customer(company: str, name: str, display: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": name, "company": company
	}, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": "Customer", "customer_name": name, "company": company
	})
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_supplier(company: str, name: str) -> str:
	existing = frappe.db.get_value("Supplier", {"supplier_name": name, "company": company
	}, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": "Supplier", "supplier_name": name, "company": company
	})
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_uom(uom_name: str) -> None:
	if uom_name and not frappe.db.exists("UOM", uom_name):
		frappe.get_doc({"doctype": "UOM", "uom_name": uom_name
	}).insert(ignore_permissions=True)


def _item_has_arabic_name_field() -> bool:
	try:
		return bool(frappe.get_meta("Item").has_field("item_name_ar"))
	except Exception:
		return False


def _ensure_construction_material_catalog(company: str) -> list[str]:
	"""Create bilingual (EN/AR) construction raw-material items for demo procurement & inventory."""
	if not frappe.db.exists("DocType", "Item"):
		return []
	has_ar = _item_has_arabic_name_field()
	item_codes: list[str] = []
	for suffix, name_en, name_ar, uom, product_type, classification in CONSTRUCTION_MATERIAL_CATALOG:
		_ensure_uom(uom)
		code = f"{DEMO_MARKER}{suffix}"
		existing = frappe.db.get_value("Item", {"item_code": code, "company": company
	}, "name")
		if existing:
			if has_ar:
				frappe.db.set_value("Item", existing, "item_name_ar", name_ar, update_modified=False)
			item_codes.append(code)
			continue
		payload: dict = {
			"doctype": "Item",
			"item_code": code,
			"item_name": name_en,
			"company": company,
			"stock_uom": uom,
			"product_type": product_type,
			"is_stock_item": 1,
			"is_purchase_item": 1,
			"is_sales_item": 0,
			"classification_code": classification
	}
		if has_ar:
			payload["item_name_ar"] = name_ar
		item = frappe.get_doc(payload)
		item.insert(ignore_permissions=True)
		item_codes.append(code)
	return item_codes


def _delete_demo_material_items(company: str, dry_run: bool) -> dict:
	if not frappe.db.exists("DocType", "Item"):
		return {"doctype": "Item", "matched": 0, "cancelled": 0, "deleted": 0
	}
	return _delete_branch_docs(
		"Item",
		{"company": company, "item_code": ["like", f"{DEMO_MARKER}MAT-%"]},
		dry_run,
	)


def _contract_title(spec: dict) -> str:
	return f"{DEMO_MARKER}{spec['code']} {spec['title_en']}"


def _already_seeded(company: str, branch: str | None = None) -> bool:
	title = _contract_title(PROJECT_SPECS[0])
	filters: dict = {"company": company, "contract_title": title
	}
	if branch:
		filters["branch"] = branch
	return bool(frappe.db.exists("Project Contract", filters))


def _delete_branch_docs(doctype: str, filters: dict, dry_run: bool) -> dict:
	if not frappe.db.exists("DocType", doctype):
		return {"doctype": doctype, "matched": 0, "cancelled": 0, "deleted": 0
	}
	names = frappe.get_all(doctype, filters=filters, pluck="name", limit=10000)
	if dry_run:
		return {"doctype": doctype, "matched": len(names), "cancelled": 0, "deleted": 0
	}
	cancelled = 0
	deleted = 0
	for name in reversed(names):
		try:
			doc = frappe.get_doc(doctype, name)
		except frappe.DoesNotExistError:
			continue
		if hasattr(doc, "docstatus") and int(doc.docstatus or 0) == 1:
			try:
				doc.cancel()
				cancelled += 1
			except Exception:
				pass
		try:
			frappe.delete_doc(doctype, name, ignore_permissions=True, force=1)
			deleted += 1
		except Exception:
			pass
	return {"doctype": doctype, "matched": len(names), "cancelled": cancelled, "deleted": deleted
	}


def _delete_for_contracts(doctype: str, contract_names: list[str], base: dict, dry_run: bool) -> dict:
	if not contract_names:
		return {"doctype": doctype, "matched": 0, "cancelled": 0, "deleted": 0
	}
	return _delete_branch_docs(doctype, {**base, "project_contract": ["in", contract_names]}, dry_run)


@frappe.whitelist(methods=["POST"])
def reset_construction_demo_for_branch(
	company: str,
	branch: str,
	dry_run: int | str = 0,
) -> dict:
	"""Remove construction demo documents scoped to one branch."""
	_assert_admin()
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found").format(company))
	if not branch or not frappe.db.exists("Branch", branch):
		frappe.throw(_("Branch {0} not found").format(branch))
	b_company = frappe.db.get_value("Branch", branch, "company")
	if b_company != company:
		frappe.throw(_("Branch does not belong to this company."))

	is_dry = cint(dry_run) == 1
	contract_names = frappe.get_all(
		"Project Contract",
		filters={"company": company, "branch": branch, "contract_title": ["like", f"{DEMO_MARKER}%"]},
		pluck="name",
	)
	scw_names = (
		frappe.get_all(
			"Subcontract Work Order",
			filters={"company": company, "branch": branch, "project_contract": ["in", contract_names]},
			pluck="name",
		)
		if contract_names
		else []
	)

	report: list[dict] = []
	base = {"company": company, "branch": branch
	}

	if scw_names:
		report.append(
			_delete_branch_docs(
				"Subcontract Payment Certificate",
				{**base, "subcontract_work_order": ["in", scw_names]},
				is_dry,
			)
		)
	report.append(_delete_branch_docs("IPC Certificate", {**base, "certificate_reference": ["like", f"{DEMO_MARKER}%"]}, is_dry))
	report.append(_delete_branch_docs("Site Daily Report", {**base, "report_reference": ["like", f"{DEMO_MARKER}%"]}, is_dry))

	for dt in (
		"Construction Claim",
		"Construction Extension of Time",
		"Construction NCR",
		"Construction HSE Incident",
		"Construction Inspection Request",
		"Construction Document Transmittal",
	):
		report.append(_delete_for_contracts(dt, contract_names, base, is_dry))

	if contract_names:
		report.append(_delete_for_contracts("Construction Change Order", contract_names, base, is_dry))
		report.append(_delete_for_contracts("Project WIP Snapshot", contract_names, base, is_dry))
		report.append(_delete_for_contracts("Subcontract Work Order", contract_names, base, is_dry))
		report.append(_delete_for_contracts("BOQ Item", contract_names, base, is_dry))

	if frappe.db.exists("DocType", "Purchase Request") and contract_names:
		report.append(_delete_for_contracts("Purchase Request", contract_names, base, is_dry))

	report.append(_delete_branch_docs("Project Contract", {**base, "contract_title": ["like", f"{DEMO_MARKER}%"]}, is_dry))

	if frappe.db.exists("DocType", "Purchase Order"):
		po_filters = {**base, "supplier": ["like", f"{DEMO_MARKER}%"]}
		report.append(_delete_branch_docs("Purchase Order", po_filters, is_dry))

	report.append(_delete_demo_material_items(company, is_dry))

	if not is_dry:
		frappe.db.commit()

	return {
		"ok": True,
		"company": company,
		"branch": branch,
		"dry_run": is_dry,
		"details": report
	}


def _seed_qa_hse_docs(
	*,
	contract,
	spec: dict,
	idx: int,
	boq_names: list[str],
	company: str,
	branch: str,
	start,
	summary: dict,
) -> None:
	boq_ref = boq_names[0] if boq_names else None
	ncr_statuses = ("Open", "Under Review", "Closed")
	for ncr_i in range(2 if idx % 3 else 1):
		ncr = frappe.get_doc(
			{
				"doctype": "Construction NCR",
				"project_contract": contract.name,
				"ncr_date": add_days(start, 30 + ncr_i * 12),
				"ncr_reference": f"{DEMO_MARKER}NCR-{spec['code']}-{ncr_i + 1
	}",
				"boq_item": boq_ref,
				"severity": ("Minor", "Major", "Critical")[ncr_i % 3],
				"description": f"Non-conformance on {spec['title_en']} — hold point {ncr_i + 1
	}.",
				"corrective_action": "CAR issued; rework and re-inspection scheduled.",
				"status": ncr_statuses[ncr_i % len(ncr_statuses)],
				"company": company,
				"branch": branch
	}
		)
		ncr.insert(ignore_permissions=True)
		summary["ncrs"] = summary.get("ncrs", 0) + 1

	hse_types = ("Near Miss", "Injury", "Property Damage", "Environmental")
	hse = frappe.get_doc(
		{
			"doctype": "Construction HSE Incident",
			"project_contract": contract.name,
			"incident_date": now_datetime(),
			"incident_type": hse_types[idx % len(hse_types)],
			"severity": ("Low", "Medium", "High", "Critical")[idx % 4],
			"location": spec["site"],
			"description": f"HSE event logged for demo portfolio — {spec['title_en']
	}.",
			"status": ("Reported", "Investigating", "Closed")[idx % 3],
			"company": company,
			"branch": branch
	}
	)
	hse.insert(ignore_permissions=True)
	summary["hse_incidents"] = summary.get("hse_incidents", 0) + 1

	ir_statuses = ("Scheduled", "In Progress", "Passed", "Failed")
	for ir_i in range(2):
		ir = frappe.get_doc(
			{
				"doctype": "Construction Inspection Request",
				"project_contract": contract.name,
				"inspection_date": add_days(start, 20 + ir_i * 18),
				"location": f"{spec['site']} — Zone {ir_i + 1
	}",
				"work_activity": ("Concrete pour", "MEP pressure test", "Steel erection")[ir_i % 3],
				"boq_item": boq_names[ir_i % len(boq_names)] if boq_names else None,
				"findings": "Demo inspection record for QA register and site compliance.",
				"status": ir_statuses[ir_i % len(ir_statuses)],
				"company": company,
				"branch": branch
	}
		)
		ir.insert(ignore_permissions=True)
		summary["inspection_requests"] = summary.get("inspection_requests", 0) + 1


def _seed_document_transmittal(
	*, contract, spec: dict, company: str, branch: str, start, summary: dict
) -> None:
	if not frappe.db.exists("DocType", "Construction Document Transmittal"):
		return
	docs = [
		("Shop drawings — structural", f"SD-{spec['code']}-STR", "B", "For Construction"),
		("RFI response pack", f"RFI-{spec['code']}-014", "A", "For Review"),
		("As-built redlines", f"AB-{spec['code']}-MEP", "0", "As Built"),
	]
	tr = frappe.get_doc(
		{
			"doctype": "Construction Document Transmittal",
			"project_contract": contract.name,
			"transmittal_date": add_days(start, 40),
			"reference_no": f"{DEMO_MARKER}CDT-{spec['code']
	}",
			"issued_by": frappe.session.user,
			"recipient_notes": "Employer / Engineer — ISO 19650 distribution (demo).",
			"status": ("Issued", "Acknowledged")[int(spec["code"]) % 2],
			"company": company,
			"branch": branch,
			"items": [
				{
					"document_title": title,
					"document_no": doc_no,
					"revision_no": rev,
					"issue_purpose": purpose,
					"remarks": "Construction demo transmittal line."
	}
				for title, doc_no, rev, purpose in docs
			]}
	)
	tr.insert(ignore_permissions=True)
	summary["document_transmittals"] = summary.get("document_transmittals", 0) + 1


def _seed_claims_eot(
	*,
	contract,
	spec: dict,
	idx: int,
	co_name: str | None,
	company: str,
	branch: str,
	start,
	end,
	summary: dict,
) -> tuple[str | None, str | None]:
	eot_name = None
	claim_name = None
	if idx % 4 == 1 and frappe.db.exists("DocType", "Construction Extension of Time"):
		eot = frappe.get_doc(
			{
				"doctype": "Construction Extension of Time",
				"project_contract": contract.name,
				"application_date": add_days(start, 90),
				"notice_reference": f"{DEMO_MARKER}EOT-{spec['code']
	}",
				"cause_category": "Late instructions / variations",
				"delay_days_claimed": 21 + idx,
				"delay_days_approved": 14 + (idx % 5),
				"revised_completion_date": add_days(end, 14),
				"related_change_order": co_name,
				"description": f"EOT application — employer delay events on {spec['title_en']
	}.",
				"status": "Approved",
				"company": company,
				"branch": branch
	}
		)
		eot.insert(ignore_permissions=True)
		eot_name = eot.name
		summary["extensions_of_time"] = summary.get("extensions_of_time", 0) + 1

	if idx % 5 == 2 and frappe.db.exists("DocType", "Construction Claim"):
		claim = frappe.get_doc(
			{
				"doctype": "Construction Claim",
				"project_contract": contract.name,
				"claim_date": add_days(start, 100),
				"claim_reference": f"{DEMO_MARKER}CLM-{spec['code']
	}",
				"claim_type": ("Cost", "Time", "Cost & Time")[idx % 3],
				"claimed_amount": flt(spec["contract_value"]) * 0.025,
				"claimed_delay_days": 10 + idx,
				"related_extension_of_time": eot_name,
				"related_change_order": co_name,
				"description": f"Contractor claim — prolongation and disruption on {spec['title_en']
	}.",
				"status": ("Submitted", "Under Review", "Accepted")[idx % 3],
				"company": company,
				"branch": branch
	}
		)
		claim.insert(ignore_permissions=True)
		claim_name = claim.name
		summary["claims"] = summary.get("claims", 0) + 1

	return eot_name, claim_name


def _seed_procurement(
	*,
	contract,
	spec: dict,
	idx: int,
	sub: str,
	boq_names: list,
	boq_meta: list[tuple[str, str]],
	material_codes: list[str],
	company: str,
	branch: str,
	base_date,
	summary: dict,
) -> None:
	if not material_codes or not boq_names:
		return
	boq_name = boq_names[0]
	cost_code = boq_meta[0][1] if boq_meta else "01.10"
	# Rotate 3 materials per project for realistic procurement mix
	line_items = []
	for line_i in range(3):
		mat_code = material_codes[(idx * 3 + line_i) % len(material_codes)]
		qty = 25 + idx * 4 + line_i * 10
		rate = 850 + (idx % 7) * 120 + line_i * 90
		line_items.append(
			{
				"item_code": mat_code,
				"qty": qty,
				"rate": rate,
				"boq_item": boq_names[line_i % len(boq_names)],
				"cost_code": boq_meta[line_i % len(boq_meta)][1] if boq_meta else cost_code
	}
		)

	if frappe.db.exists("DocType", "Purchase Request"):
		try:
			pr = frappe.get_doc(
				{
					"doctype": "Purchase Request",
					"company": company,
					"branch": branch,
					"project_contract": contract.name,
					"required_by": add_days(base_date, 21),
					"requester": frappe.session.user,
					"reference": f"{DEMO_MARKER}PR-{spec['code']
	}",
					"items": [{"item_code": row["item_code"], "qty": row["qty"], "boq_item": row["boq_item"], "cost_code": row["cost_code"]} for row in line_items]
	}
			)
			pr.insert(ignore_permissions=True)
			summary["purchase_requests"] = summary.get("purchase_requests", 0) + 1
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Construction demo: PR {spec['code']}")

	if frappe.db.exists("DocType", "Purchase Order"):
		try:
			po = frappe.get_doc(
				{
					"doctype": "Purchase Order",
					"company": company,
					"branch": branch,
					"project_contract": contract.name,
					"supplier": sub,
					"posting_date": add_days(base_date, -14 - idx),
					"items": [
						{
							"item": row["item_code"],
							"item_code": row["item_code"],
							"qty": row["qty"],
							"rate": row["rate"],
							"boq_item": row["boq_item"],
							"cost_code": row["cost_code"]
	}
						for row in line_items
					]}
			)
			po.insert(ignore_permissions=True)
			if po.meta.is_submittable and po.docstatus == 0:
				po.submit()
			summary["purchase_orders"] = summary.get("purchase_orders", 0) + 1
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Construction demo: PO {spec['code']}")


def seed_construction_portfolio_demo(
	company: str,
	branch: str | None = None,
	force: int | str | None = 0,
) -> dict:
	"""Seed twenty construction projects with full portfolio demo (BOQ, IPC, QA/HSE, claims, procurement)."""
	_assert_admin()
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found").format(company))

	branch = _resolve_branch(company, branch)
	currency = _company_currency(company)
	expense_gl, payable_gl = _gl_defaults(company)

	if _already_seeded(company, branch) and not cint(force):
		return {
			"ok": True,
			"skipped": True,
			"message": _("Construction demo data already exists for this branch. Reset branch demo data first, or use force=1."),
			"contracts": frappe.get_all(
				"Project Contract",
				filters={"company": company, "branch": branch, "contract_title": ["like", f"{DEMO_MARKER}%"]},
				pluck="name",
			)}

	summary: dict = {
		"ok": True,
		"skipped": False,
		"company": company,
		"branch": branch,
		"project_count": PROJECT_COUNT,
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
		"purchase_requests": 0,
		"ncrs": 0,
		"hse_incidents": 0,
		"inspection_requests": 0,
		"document_transmittals": 0,
		"extensions_of_time": 0,
		"claims": 0,
		"gl_posted_spc": 0,
		"material_items": 0
	}

	owners: list[str] = []
	subs: list[str] = []
	for i, spec in enumerate(PROJECT_SPECS, start=1):
		owners.append(
			_ensure_customer(
				company,
				f"{DEMO_MARKER}OWNER-{i:02d}",
				f"Owner {i} — {spec['title_en'][:48]}",
			)
		)
	for i in range(1, 9):
		subs.append(_ensure_supplier(company, f"{DEMO_MARKER}SUB-{i:02d}"))
	summary["customers"] = owners
	summary["suppliers"] = subs

	material_codes = _ensure_construction_material_catalog(company)
	summary["material_items"] = len(material_codes)
	base_date = getdate(today())

	for idx, spec in enumerate(PROJECT_SPECS):
		owner = owners[idx]
		sub = subs[idx % len(subs)]
		title = _contract_title(spec)
		start = add_months(base_date, -8 + (idx % 6))
		end = add_months(start, 16 + (idx % 8))
		status = _contract_status(idx)

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
				"status": status,
				"company": company,
				"branch": branch
	}
		)
		contract.insert(ignore_permissions=True)
		if contract.meta.is_submittable:
			contract.submit()
		summary["contracts"].append(contract.name)

		boq_names: list[str] = []
		boq_meta: list[tuple[str, str]] = []
		for line_idx, (desc, cost_code, qty, unit_cost, lump) in enumerate(BOQ_LINE_TEMPLATES):
			if lump:
				uc = flt(lump) / max(flt(qty), 1)
				planned = flt(lump)
				ac = planned * (1.22 if line_idx in (1, 3) else 0.55 + 0.08 * line_idx)
			else:
				uc = unit_cost
				planned = flt(qty) * flt(unit_cost)
				ac = planned * (1.18 if line_idx in (1, 3) else 0.42 + 0.07 * line_idx)
			boq = frappe.get_doc(
				{
					"doctype": "BOQ Item",
					"project_contract": contract.name,
					"section_name": f"Section {line_idx + 1
	}",
					"cost_code": cost_code,
					"item_description": desc,
					"quantity": qty,
					"unit_of_measure": "m³" if line_idx == 0 else "Nos",
					"unit_cost": uc,
					"actual_cost": ac,
					"completion_percent": min(88, 12 * (line_idx + 1) + idx * 2),
					"company": company,
					"branch": branch
	}
			)
			boq.insert(ignore_permissions=True)
			boq_names.append(boq.name)
			boq_meta.append((boq.name, cost_code))
			summary["boq_items"] += 1

		scw = frappe.get_doc(
			{
				"doctype": "Subcontract Work Order",
				"project_contract": contract.name,
				"subcontractor": sub,
				"scope_of_work": f"Subcontract package — {spec['title_en']
	}",
				"contract_value": flt(spec["contract_value"]) * 0.35,
				"progress_percent": IPC_PROGRESS_STEPS[-1],
				"status": "Active" if status == "Active" else "Closed",
				"company": company,
				"branch": branch
	}
		)
		scw.insert(ignore_permissions=True)
		summary["subcontract_work_orders"] += 1

		last_ipc_name = None
		for step_i, pct in enumerate(IPC_PROGRESS_STEPS):
			ipc_date = add_days(add_months(start, step_i + 2), 5)
			is_last = step_i == len(IPC_PROGRESS_STEPS) - 1
			ipc_status = "Posted" if is_last and idx % 3 == 0 else "Certified"
			ipc_data = {
				"doctype": "IPC Certificate",
				"project_contract": contract.name,
				"ipc_date": ipc_date,
				"period_from": add_days(ipc_date, -30),
				"period_to": ipc_date,
				"employer_certificate_ref": f"ENG/IPC/{spec['code']}/{step_i + 1
	}",
				"boq_completion_percent": pct,
				"status": ipc_status,
				"company": company,
				"branch": branch,
				"certificate_reference": f"{DEMO_MARKER}IPC-{spec['code']}-{step_i + 1}"
	}
			ipc = frappe.get_doc(ipc_data)
			ipc.insert(ignore_permissions=True)
			last_ipc_name = ipc.name
			summary["ipc_certificates"] += 1

		if expense_gl and payable_gl:
			for cert_i, fraction in enumerate((0.25, 0.55, 0.78)):
				cert_date = add_days(add_months(start, 3 + cert_i), 10)
				certified = flt(scw.contract_value) * fraction
				spc = frappe.get_doc(
					{
						"doctype": "Subcontract Payment Certificate",
						"subcontract_work_order": scw.name,
						"certificate_date": cert_date,
						"certified_amount": certified,
						"previously_paid": certified * 0.35 if cert_i else 0,
						"retention_percent": 5,
						"status": "Draft",
						"expense_account": expense_gl,
						"payable_account": payable_gl,
						"company": company,
						"branch": branch,
						"payment_reference": f"{DEMO_MARKER}SPC-{spec['code']}-{cert_i + 1}"
	}
				)
				spc.insert(ignore_permissions=True)
				if spc.meta.is_submittable and cert_i < 2:
					try:
						spc.submit()
						summary["gl_posted_spc"] += 1
					except Exception:
						frappe.log_error(frappe.get_traceback(), f"Construction demo: SPC submit failed for {spc.name}")
				summary["subcontract_payment_certificates"] += 1

		for day_offset in SITE_REPORT_OFFSETS:
			sdr = frappe.get_doc(
				{
					"doctype": "Site Daily Report",
					"project": contract.name,
					"report_date": add_days(base_date, -day_offset - idx),
					"boq_item": boq_names[0] if boq_names else None,
					"weather": ("Clear / 28°C", "Windy / 24°C", "Light rain / 22°C")[day_offset % 3],
					"work_summary": f"Progress on {spec['title_en']
	} — pour, steel fix, QA hold points.",
					"labor_count": 45 + idx * 6,
					"equipment_hours": 32 + idx * 3,
					"material_consumed_cost": 125_000 + idx * 12_000,
					"company": company,
					"branch": branch,
					"report_reference": f"{DEMO_MARKER}SDR-{spec['code']}-{day_offset}"
	}
			)
			sdr.insert(ignore_permissions=True)
			summary["site_daily_reports"] += 1

		co_name = None
		if idx % 2 == 0:
			co = frappe.get_doc(
				{
					"doctype": "Construction Change Order",
					"project_contract": contract.name,
					"order_date": add_days(start, 45),
					"title": f"VO-{spec['code']
	} — scope adjustment",
					"contract_clause_reference": "Sub-Clause 13.3",
					"description": "Employer variation — additional MEP scope and revised programme.",
					"cost_impact": flt(spec["contract_value"]) * 0.03,
					"time_impact_days": 14 + (idx % 7),
					"status": "Approved",
					"company": company,
					"branch": branch
	}
			)
			co.insert(ignore_permissions=True)
			co_name = co.name
			summary["change_orders"] += 1

		_seed_claims_eot(
			contract=contract,
			spec=spec,
			idx=idx,
			co_name=co_name,
			company=company,
			branch=branch,
			start=start,
			end=end,
			summary=summary,
		)
		_seed_qa_hse_docs(
			contract=contract,
			spec=spec,
			idx=idx,
			boq_names=boq_names,
			company=company,
			branch=branch,
			start=start,
			summary=summary,
		)
		_seed_document_transmittal(
			contract=contract,
			spec=spec,
			company=company,
			branch=branch,
			start=start,
			summary=summary,
		)
		_seed_procurement(
			contract=contract,
			spec=spec,
			idx=idx,
			sub=sub,
			boq_names=boq_names,
			boq_meta=boq_meta,
			material_codes=material_codes,
			company=company,
			branch=branch,
			base_date=base_date,
			summary=summary,
		)

		last_ipc_amount = frappe.db.get_value("IPC Certificate", last_ipc_name, "net_amount") if last_ipc_name else 0
		wip = frappe.get_doc(
			{
				"doctype": "Project WIP Snapshot",
				"project_contract": contract.name,
				"snapshot_date": base_date,
				"cost_to_date": flt(spec["contract_value"]) * (0.38 + (idx % 5) * 0.04),
				"revenue_recognized": flt(last_ipc_amount or 0) * 0.85,
				"company": company,
				"branch": branch,
				"snapshot_reference": f"{DEMO_MARKER}WIP-{spec['code']}"
	}
		)
		wip.insert(ignore_permissions=True)
		summary["wip_snapshots"] += 1

		try:
			from omnexa_construction.contract_financials import refresh_project_contract_financials

			refresh_project_contract_financials(contract.name)
		except Exception:
			pass

	frappe.db.commit()
	summary["message"] = _(
		"Created {0} construction projects with BOQ, IPC, {1} bilingual material items, QA/HSE, claims, and procurement."
	).format(len(summary["contracts"]), summary.get("material_items", 0))
	return summary
