from __future__ import annotations

import re
from contextlib import contextmanager
from pathlib import Path

import frappe

MODULE = "Omnexa Construction"
FORMS_DIR = Path(__file__).resolve().parent / "print_templates"
WIZARD_DIR = Path(__file__).resolve().parents[1] / "wizard" / "print_templates"


def read_a4_base_css() -> str:
	path = FORMS_DIR / "_a4_base.css.html"
	return path.read_text(encoding="utf-8") if path.exists() else ""


def strip_inline_styles(html: str) -> str:
	"""Remove duplicate inline <style> blocks; unified A4 CSS is injected by patch."""
	return re.sub(r"<style[^>]*>.*?</style>\s*", "", html, count=0, flags=re.DOTALL | re.IGNORECASE)


def compose_print_html(body_html: str, *, inject_base: bool = True) -> str:
	body = strip_inline_styles(body_html) if inject_base else body_html
	base = read_a4_base_css() if inject_base else ""
	if base and base.strip() in body:
		return body
	return f"{base}\n{body}".strip()


@contextmanager
def _allow_standard_print_format_writes():
	"""Print Format.validate blocks standard=Yes unless in_migrate/install/test."""
	prev = bool(getattr(frappe.flags, "in_migrate", False))
	frappe.flags.in_migrate = True
	try:
		yield
	finally:
		frappe.flags.in_migrate = prev


def ensure_print_format(
	name: str,
	doctype: str,
	html: str,
	*,
	lang: str | None = None,
	standard: str = "Yes",
) -> None:
	values = {
		"html": html,
		"custom_format": 1,
		"print_format_type": "Jinja",
		"disabled": 0,
		"standard": standard,
	}
	if lang:
		values["default_print_language"] = lang

	with _allow_standard_print_format_writes():
		if frappe.db.exists("Print Format", name):
			frappe.db.set_value("Print Format", name, values, update_modified=True)
			return
		frappe.get_doc(
			{
				"doctype": "Print Format",
				"name": name,
				"doc_type": doctype,
				"module": MODULE,
				**values,
			}
		).insert(ignore_permissions=True)


def _ensure_print(name: str, doctype: str, html: str, *, lang: str | None = None) -> None:
	ensure_print_format(name, doctype, html, lang=lang)


def sync_all_a4_print_formats() -> dict:
	"""Idempotent sync of all construction A4 print formats."""
	stats = {"updated": 0, "formats": []}

	arabic_forms = (
		("Construction Work Approval — AR", "Construction Work Approval Request", "work_approval_ar.html", "ar"),
		("Construction Material Approval — AR", "Construction Material Approval Request", "material_approval_ar.html", "ar"),
		("Contractor Account Statement — AR", "Contractor Account Statement", "contractor_account_ar.html", "ar"),
		("Construction Fines Statement — AR", "Construction Fines Statement", "fines_statement_ar.html", "ar"),
		("Construction Work Delay — AR", "Construction Work Delay Notice", "work_delay_ar.html", "ar"),
		("IPC Certificate — AR (مستخلص مقاولات)", "IPC Certificate", "ipc_certificate_ar.html", "ar"),
		("Project Contract — AR (ملخص العقد)", "Project Contract", "project_contract_ar.html", "ar"),
	)

	for name, doctype, filename, lang in arabic_forms:
		if not frappe.db.exists("DocType", doctype):
			continue
		raw = (FORMS_DIR / filename).read_text(encoding="utf-8")
		html = compose_print_html(raw)
		_ensure_print(name, doctype, html, lang=lang)
		stats["updated"] += 1
		stats["formats"].append(name)

	if frappe.db.exists("DocType", "Project Contract"):
		raw = (FORMS_DIR / "project_contract_ar.html").read_text(encoding="utf-8")
		html = compose_print_html(raw)
		_ensure_print("Project Contract — Summary", "Project Contract", html)
		stats["updated"] += 1
		stats["formats"].append("Project Contract — Summary")

	setup_prints = (
		("Construction Setup — Summary", "setup_summary.html"),
		("Construction Setup — BOQ Schedule", "setup_boq_schedule.html"),
		("Construction Setup — IPC Schedule", "setup_ipc_schedule.html"),
		("Construction Setup — Phase Delivery", "setup_phase_delivery.html"),
	)
	if frappe.db.exists("DocType", "Construction Project Setup"):
		for name, filename in setup_prints:
			raw = (WIZARD_DIR / filename).read_text(encoding="utf-8")
			html = compose_print_html(raw)
			_ensure_print(name, "Construction Project Setup", html)
			stats["updated"] += 1
			stats["formats"].append(name)

	frappe.clear_cache(doctype="Print Format")
	return stats
