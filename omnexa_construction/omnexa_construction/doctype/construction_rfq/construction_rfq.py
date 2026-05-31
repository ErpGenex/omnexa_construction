# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConstructionRFQ(Document):
	def validate(self):
		self._rollup_items()
		self._score_quotes()

	def _rollup_items(self) -> None:
		total = 0.0
		for row in self.items or []:
			row.amount = flt(row.quantity) * flt(row.estimated_rate)
			total += flt(row.amount)
		self.estimated_total = total

	def _score_quotes(self) -> None:
		quotes = [q for q in (self.supplier_quotes or []) if flt(q.quoted_amount) > 0]
		if not quotes:
			return
		min_amt = min(flt(q.quoted_amount) for q in quotes)
		min_lead = min(flt(q.lead_time_days) or 999 for q in quotes)
		self.lowest_quote = min_amt
		best = None
		best_score = -1.0
		for q in quotes:
			price = 100.0 * min_amt / flt(q.quoted_amount) if flt(q.quoted_amount) else 0
			lead = flt(q.lead_time_days) or 30
			lead_score = 100.0 * min_lead / lead if lead else 50
			compliance = flt(q.compliance_score) or 70
			total = 0.5 * price + 0.3 * compliance + 0.2 * lead_score
			q.price_score = price
			q.lead_time_score = lead_score
			q.total_score = total
			q.is_recommended = 0
			if total > best_score:
				best_score = total
				best = q
		if best:
			best.is_recommended = 1
			self.recommended_supplier = best.supplier
