from __future__ import annotations

from frappe import _
from frappe.utils import flt, fmt_money


def suggest_contract_terms(setup, *, replace: bool = False) -> int:
	"""Build realistic contract clauses from setup BOQ, IPC, and commercial fields."""
	if setup.contract_terms and not replace:
		return 0
	if replace:
		setup.set("contract_terms", [])

	currency = setup.contract_currency or "EGP"
	value = fmt_money(setup.estimated_contract_value, currency=currency)
	ipc_count = len(setup.ipc_plan or [])
	phases = ", ".join(f"{p.phase_code} ({flt(p.weight_percent)}%)" for p in (setup.phases or [])[:6])

	clauses = [
		(
			"Scope",
			_("Contract Scope"),
			_(
				"The Contractor shall design, supply, install, test, and commission the works for "
				"<b>{0}</b> at <b>{1}</b> ({2} / {3}) in accordance with the BOQ, specifications, "
				"drawings, and the governing form <b>{4}</b>."
			).format(
				setup.contract_title or setup.name,
				setup.site_location or _("site location as per drawings"),
				setup.building_type or "",
				setup.project_segment or "",
				setup.governing_standard or _("contract conditions"),
			),
			10,
		),
		(
			"BOQ & Schedule",
			_("Bill of Quantities — Contract Appendix"),
			_(
				"The priced BOQ attached to Construction Project Setup <b>{0}</b> (revision {1}) "
				"forms an integral part of the contract. Contract price (excl. approved variations): "
				"<b>{2}</b>. Planned start: {3}; planned completion: {4}. "
				"Delivery phases: {5}."
			).format(
				setup.name,
				setup.setup_revision or 1,
				value,
				setup.planned_start or "—",
				setup.planned_completion or "—",
				phases or "—",
			),
			20,
		),
		(
			"Payment & IPC",
			_("Interim Payment Certificates (IPC)"),
			_(
				"Payment shall follow the IPC schedule ({0} certificates) tied to measured progress "
				"and consultant/engineer certification. Default IPC discount: {1}%. "
				"Each IPC shall reference approved BOQ items, work approvals, and material approvals "
				"where applicable."
			).format(ipc_count, flt(setup.default_discount_percent)),
			30,
		),
		(
			"Retention & Advance",
			_("Retention & Advance Payment"),
			_(
				"Retention at <b>{0}%</b> shall be deducted from certified IPC amounts until release "
				"per contract conditions. Advance payment: {1}% ({2}). "
				"Advance recovery shall be proportional to certified works unless otherwise agreed."
			).format(
				flt(setup.retention_percent) or 5,
				flt(setup.advance_payment_percent),
				fmt_money(setup.advance_payment_amount, currency=currency) if setup.advance_payment_amount else _("as per LOA"),
			),
			40,
		),
		(
			"Liquidated Damages",
			_("Delay Damages (LD)"),
			_(
				"Liquidated damages for delay: <b>{0}</b> per day, capped at <b>{1}%</b> of the contract price, "
				"without prejudice to other contractual remedies."
			).format(
				fmt_money(setup.liquidated_damages_per_day, currency=currency)
				if setup.liquidated_damages_per_day
				else _("as per particular conditions"),
				flt(setup.liquidated_damages_cap_percent) or 10,
			),
			50,
		),
		(
			"Quality & Approvals",
			_("Quality, ITP, Work & Material Approvals"),
			_(
				"No concealed works without inspection. Materials shall be approved prior to incorporation. "
				"Work approval requests and material approval requests shall be submitted per the Inspection "
				"and Test Plan (ITP). Mock-ups and third-party QA witness points apply where listed in the BOQ."
			),
			60,
		),
		(
			"Handover",
			_("Testing, Commissioning & Handover"),
			_(
				"Handover shall be by phase where defined. As-built documentation, O&M manuals, "
				"performance tests, and snag-list closure are prerequisites to final completion "
				"and performance certificate / final account."
			),
			70,
		),
		(
			"Variations",
			_("Variations & Change Orders"),
			_(
				"Variations shall be instructed in writing (Change Order / FIDIC Notice as applicable). "
				"No work outside the approved BOQ without prior authorization. "
				"Revised contract value = base contract + approved change orders."
			),
			80,
		),
	]

	for group, title, text, order in clauses:
		setup.append(
			"contract_terms",
			{
				"clause_group": group,
				"clause_title": title,
				"clause_text": text,
				"sort_order": order,
			},
		)
	return len(clauses)
