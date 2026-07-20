from __future__ import annotations

"""Map wizard / template governing labels to Project Contract Select options."""

GOVERNING_CONTRACT_FORM_OPTIONS: tuple[str, ...] = (
	"FIDIC 2017 Red Book (Building & Engineering)",
	"FIDIC 2017 Yellow Book (M&E Design-Build)",
	"FIDIC 2017 Silver Book (EPC/Turnkey)",
	"FIDIC 1999 Suite (Red/Yellow/Silver)",
	"NEC4 ECC",
	"AIA / ConsensusDocs",
	"Other / Bespoke",
)

_DEFAULT = GOVERNING_CONTRACT_FORM_OPTIONS[0]

_ALIASES: dict[str, str] = {
	"fidic 2017 red book": _DEFAULT,
	"fidic red book": _DEFAULT,
	"red book": _DEFAULT,
	"fidic 2017 yellow book": GOVERNING_CONTRACT_FORM_OPTIONS[1],
	"fidic yellow book": GOVERNING_CONTRACT_FORM_OPTIONS[1],
	"yellow book": GOVERNING_CONTRACT_FORM_OPTIONS[1],
	"fidic 2017 silver book": GOVERNING_CONTRACT_FORM_OPTIONS[2],
	"fidic silver book": GOVERNING_CONTRACT_FORM_OPTIONS[2],
	"silver book": GOVERNING_CONTRACT_FORM_OPTIONS[2],
	"fidic 1999": GOVERNING_CONTRACT_FORM_OPTIONS[3],
	"fidic 1999 suite": GOVERNING_CONTRACT_FORM_OPTIONS[3],
	"nec4": GOVERNING_CONTRACT_FORM_OPTIONS[4],
	"nec4 ecc": GOVERNING_CONTRACT_FORM_OPTIONS[4],
	"aia": GOVERNING_CONTRACT_FORM_OPTIONS[5],
	"consensusdocs": GOVERNING_CONTRACT_FORM_OPTIONS[5]
	}


def normalize_governing_standard(
	value: str | None,
	*,
	contract_type: str | None = None,
) -> str:
	"""Return a value allowed on Project Contract.governing_standard (Select)."""
	raw = (value or "").strip()
	if not raw:
		return _default_for_contract_type(contract_type)

	if raw in GOVERNING_CONTRACT_FORM_OPTIONS:
		return raw

	key = raw.lower()
	if key in _ALIASES:
		return _ALIASES[key]

	# Prefix / contains match for legacy template strings
	if "silver" in key:
		return GOVERNING_CONTRACT_FORM_OPTIONS[2]
	if "yellow" in key:
		return GOVERNING_CONTRACT_FORM_OPTIONS[1]
	if "1999" in key:
		return GOVERNING_CONTRACT_FORM_OPTIONS[3]
	if "nec" in key:
		return GOVERNING_CONTRACT_FORM_OPTIONS[4]
	if "aia" in key or "consensus" in key:
		return GOVERNING_CONTRACT_FORM_OPTIONS[5]
	if "red" in key or "fidic" in key:
		return _DEFAULT

	return _default_for_contract_type(contract_type)


def _default_for_contract_type(contract_type: str | None) -> str:
	ct = (contract_type or "").strip().lower()
	if "turnkey" in ct or "epc" in ct:
		return GOVERNING_CONTRACT_FORM_OPTIONS[2]
	return _DEFAULT
