# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Fix Number Card filters that break Project Contract list (Invalid filter: =)."""


def execute():
	import frappe

	from omnexa_construction.patches.v1_0.ensure_construction_portfolio_cards import (
		PORTFOLIO_CARDS,
		_upsert_number_card,
	)
	from omnexa_construction.utils.number_card_filters import fix_number_cards_for_doctype

	# Re-sync portfolio cards with 4-tuple filters
	for label, doctype, filters in PORTFOLIO_CARDS:
		from omnexa_construction.utils.number_card_filters import normalize_number_card_filters

		_upsert_number_card(label, doctype, normalize_number_card_filters(doctype, filters))

	fix_number_cards_for_doctype("Project Contract")
	frappe.db.commit()
