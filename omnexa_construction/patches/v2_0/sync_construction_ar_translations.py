# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Sync DocType/report labels into translations/ar.csv (target 500+ entries)."""

from __future__ import annotations

from pathlib import Path

import frappe

MODULE = "Omnexa Construction"
APP = "omnexa_construction"

# Common construction ERP glossary (English → Arabic)
GLOSSARY: dict[str, str] = {
	"Project Contract": "عقد المشروع",
	"BOQ Item": "بند جدول الكميات",
	"Company": "الشركة",
	"Branch": "الفرع",
	"Status": "الحالة",
	"Description": "الوصف",
	"Date": "التاريخ",
	"Amount": "المبلغ",
	"Quantity": "الكمية",
	"Rate": "السعر",
	"Location": "الموقع",
	"Contract": "العقد",
	"Supplier": "المورد",
	"Customer": "العميل",
	"Client": "العميل",
	"Contractor": "المقاول",
	"Subcontractor": "مقاول الباطن",
	"Project Manager": "مدير المشروع",
	"Site Engineer": "مهندس موقع",
	"Draft": "مسودة",
	"Approved": "معتمد",
	"Rejected": "مرفوض",
	"Closed": "مغلق",
	"Open": "مفتوح",
	"Submitted": "مُرسَل",
	"Active": "نشط",
	"Cancelled": "ملغى",
	"Overview": "نظرة عامة",
	"Details": "التفاصيل",
	"Remarks": "ملاحظات",
	"Reference": "المرجع",
	"Title": "العنوان",
	"Type": "النوع",
	"Severity": "الخطورة",
	"Subject": "الموضوع",
	"Question": "السؤال",
	"Response": "الرد",
	"Discipline": "التخصص",
	"Due Date": "تاريخ الاستحقاق",
	"Target Close Date": "تاريخ الإغلاق المستهدف",
	"Actual Close Date": "تاريخ الإغلاق الفعلي",
	"Assigned To": "مُسند إلى",
	"Chairperson": "رئيس الاجتماع",
	"Attendees": "الحاضرون",
	"Agenda": "جدول الأعمال",
	"Decisions": "القرارات",
	"Action Items": "بنود العمل",
	"Period Start": "بداية الفترة",
	"Period End": "نهاية الفترة",
	"Metric": "المؤشر",
	"Target": "المستهدف",
	"Actual": "الفعلي",
	"Unit": "الوحدة",
	"Parameter": "المعامل",
	"Measured Value": "القيمة المقاسة",
	"Limit": "الحد",
	"Compliance": "الامتثال",
	"Compliant": "ممتثل",
	"Non-Compliant": "غير ممتثل",
	"Review": "مراجعة",
	"Recipient": "المستلم",
	"Role / Organization": "الدور / الجهة",
	"Action": "الإجراء",
	"Acknowledged": "تم الإقرار",
	"For Review": "للمراجعة",
	"For Approval": "للاعتماد",
	"For Information": "للعلم",
	"For Construction": "للتنفيذ",
	"Leading": "استباقي",
	"Lagging": "تراجعي",
	"On Track": "على المسار",
	"At Risk": "معرض للخطر",
	"Off Track": "خارج المسار",
	"Held": "عُقد",
	"Noise": "ضوضاء",
	"Dust": "غبار",
	"Water Quality": "جودة المياه",
	"Air Quality": "جودة الهواء",
	"Vibration": "اهتزاز",
	"Management Review": "مراجعة الإدارة",
	"Safety KPI": "مؤشر سلامة",
	"Environmental Monitoring": "مراقبة بيئية",
	"Change Order BOQ Line": "بند BOQ لأمر التغيير",
	"Procore Project ID": "معرف مشروع Procore",
	"Aconex Project ID": "معرف مشروع Aconex",
	"BOQ Applied": "تم تطبيق BOQ",
	"MIDP Reference": "مرجع MIDP",
	"PM Risk Register": "سجل مخاطر PM",
	"Back-to-Back LD": "LD متوازٍ",
	"Recipients Matrix": "مصفوفة المستلمين"
	}


def _csv_path() -> Path:
	return Path(frappe.get_app_path(APP)) / "translations" / "ar.csv"


def _load_existing(path: Path) -> dict[str, str]:
	out: dict[str, str] = {}
	if not path.exists():
		return out
	for line in path.read_text(encoding="utf-8").splitlines():
		line = line.strip()
		if not line or line.startswith("#"):
			continue
		parts = [p.strip().strip('"') for p in line.split(",", 1)]
		if len(parts) == 2 and parts[0]:
			out[parts[0]] = parts[1]
	return out


def _collect_labels() -> set[str]:
	labels: set[str] = set(GLOSSARY.keys())
	for dt in frappe.get_all("DocType", filters={"module": MODULE
	}, pluck="name"):
		meta = frappe.get_meta(dt)
		labels.add(meta.name)
		for df in meta.fields:
			if df.label:
				labels.add(df.label)
			if df.options and df.fieldtype == "Select":
				for opt in (df.options or "").split("\n"):
					opt = opt.strip()
					if opt:
						labels.add(opt)
	for report in frappe.get_all("Report", filters={"module": MODULE
	}, fields=["name", "report_name"]):
		labels.add(report.name)
		if report.report_name:
			labels.add(report.report_name)
	for page in frappe.get_all("Page", filters={"module": MODULE
	}, pluck="title"):
		if page:
			labels.add(page)
	return {lbl for lbl in labels if lbl and not lbl.startswith("tab_")}


def execute():
	path = _csv_path()
	existing = _load_existing(path)
	labels = _collect_labels()
	merged = dict(existing)
	for label in labels:
		if label in merged:
			continue
		merged[label] = GLOSSARY.get(label, existing.get(label, label))
	path.parent.mkdir(parents=True, exist_ok=True)
	lines = [f'"{k}","{v}"' for k, v in sorted(merged.items(), key=lambda x: x[0].lower())]
	path.write_text("\n".join(lines) + "\n", encoding="utf-8")
	frappe.logger(APP).info("ar.csv synced: %s entries", len(merged))
