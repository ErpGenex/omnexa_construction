# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""ISO 19650-style CDE document naming validation."""

from __future__ import annotations

import re

import frappe
from frappe import _

# Project-Originator-Type-Number-Revision (simplified)
DEFAULT_PATTERN = re.compile(r"^[A-Z0-9]{2,8}-[A-Z0-9]{2,6}-[A-Z]{2,6}-\d{3,6}-[A-Z]$", re.IGNORECASE)


def validate_cde_document_number(doc) -> None:
	if not doc.get("naming_convention"):
		return
	pattern = _pattern_from_convention(doc.naming_convention)
	candidate = doc.document_number or ""
	if not pattern.match(candidate.strip()):
		frappe.throw(
			_(
				"Document number '{0}' does not match naming convention '{1}' (example: PRJ-CTR-DRW-0001-A)."
			).format(candidate, doc.naming_convention),
			title=_("CDE Naming"),
		)


def _pattern_from_convention(convention: str) -> re.Pattern:
	convention = (convention or "").strip().upper()
	if convention == "STRICT":
		return DEFAULT_PATTERN
	if convention == "RELAXED":
		return re.compile(r"^[A-Z0-9][A-Z0-9\-_.]{4,40}$", re.IGNORECASE)
	return DEFAULT_PATTERN


def validate_cde_document_doc(doc, method=None) -> None:
	if doc.meta.has_field("naming_convention"):
		validate_cde_document_number(doc)
