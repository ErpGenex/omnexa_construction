from __future__ import annotations

"""Full turnkey BOQ line packs (CSI 00–17) for all project types."""

from omnexa_construction.wizard.template_loader import (
	RES_BLD_LINES,
	URBAN_ROAD_LINES,
	VILLA_LINES,
	_line,
)


def _merge_lines(*groups: list[dict], skip: frozenset[str] | None = None) -> list[dict]:
	"""Merge line lists; later groups override earlier by cost_code."""
	skip = skip or frozenset()
	by_code: dict[str, dict] = {}
	for group in groups:
		for row in group:
			code = row.get("cost_code")
			if not code or code in skip:
				continue
			by_code[code] = dict(row)
	return sorted(by_code.values(), key=lambda r: r["cost_code"])


def _building_common_extras() -> list[dict]:
	return [
		_line("04", "Roof & Waterproofing", "04 Roof", is_group=1, trade="TRD-FACADE"),
		_line("04.10", "Roof insulation & waterproofing", "04 Roof", parent="04", uom="m²", base_qty=1.05, driver="GFA", unit_cost=520, trade="TRD-FACADE"),
		_line("06", "Internal Partitions & Ceilings", "06 Partitions", is_group=1, trade="TRD-FIN"),
		_line("06.10", "Drywall partitions", "06 Partitions", parent="06", uom="m²", base_qty=0.35, driver="GFA", unit_cost=420, trade="TRD-FIN"),
		_line("08", "Joinery & Fixtures", "08 Joinery", is_group=1, trade="TRD-FIN"),
		_line("08.10", "Doors & built-in joinery", "08 Joinery", parent="08", uom="No", base_qty=0.08, driver="UNITS", unit_cost=8500, trade="TRD-FIN"),
		_line("14", "Roads & Paving (within plot)", "14 Roads", is_group=1, trade="TRD-EXT"),
		_line("14.10", "Internal roads & parking", "14 Roads", parent="14", uom="m²", base_qty=0.15, driver="PLOT", unit_cost=680, trade="TRD-EXT"),
		_line("16", "Utilities Connections", "16 Utilities", is_group=1, trade="TRD-PIPE"),
		_line("16.10", "Off-site utility tie-ins allowance", "16 Utilities", parent="16", uom="ls", base_qty=1, driver="FIXED", unit_cost=280000, trade="TRD-PIPE"),
		_line("17", "Provisional Sums / Contingency", "17 Contingency", is_group=1),
		_line("17.10", "Design contingency (5%)", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=350000),
	]


HOSPITAL_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("00.20", "Healthcare infection control preliminaries", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=520000),
		_line("02.30", "Waterproofing & tanking (medical)", "02 Substructure", parent="02", uom="m²", base_qty=0.4, driver="GFA", unit_cost=580, trade="TRD-SUB"),
		_line("09.10", "Medical gas & plumbing systems", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="BED_COUNT / 25", unit_cost=850000, trade="TRD-MEP-P"),
		_line("09.20", "Clean room plumbing", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 400", unit_cost=420000, trade="TRD-MEP-P"),
		_line("10.10", "HVAC with HEPA / filtration", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 180", unit_cost=620000, trade="TRD-MEP-H"),
		_line("11.10", "Power, ELV & nurse call", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="BED_COUNT / 30", unit_cost=720000, trade="TRD-MEP-E"),
		_line("11.20", "Generator & UPS (critical)", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="BED_COUNT / 50", unit_cost=950000, trade="TRD-MEP-E"),
		_line("07.10", "Hygiene finishes (floors/walls)", "07 Finishes", parent="07", uom="m²", base_qty=1.1, driver="GFA", unit_cost=1200, trade="TRD-FIN"),
		_line("15.10", "Medical equipment commissioning", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=480000),
	],
	skip=frozenset({"09.10", "10.10", "11.10", "07.10", "07.20", "15.10"}),
)

SCHOOL_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("00.20", "School safety & temporary facilities", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=320000),
		_line("01.10", "Bulk excavation", "01 Earthworks", parent="01", uom="m³", base_qty=0.6, driver="PLOT", unit_cost=95, trade="TRD-EARTH"),
		_line("09.10", "Plumbing for classrooms & labs", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="UNITS / 20", unit_cost=380000, trade="TRD-MEP-P"),
		_line("10.10", "Classroom & lab HVAC", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 400", unit_cost=380000, trade="TRD-MEP-H"),
		_line("11.10", "Power, data & PA system", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 380", unit_cost=420000, trade="TRD-MEP-E"),
		_line("07.10", "Classroom & lab finishes", "07 Finishes", parent="07", uom="m²", base_qty=0.95, driver="GFA", unit_cost=780, trade="TRD-FIN"),
		_line("13.10", "Playgrounds & sports courts", "13 External", parent="13", uom="m²", base_qty=0.3, driver="PLOT", unit_cost=520, trade="TRD-EXT"),
		_line("13.20", "Boundary wall & gates", "13 External", parent="13", uom="m", base_qty=0.08, driver="PLOT", unit_cost=4200, trade="TRD-EXT"),
	],
	skip=frozenset({"09.10", "10.10", "11.10", "07.10", "07.20", "13.10"}),
)

UNIVERSITY_FULL_LINES = _merge_lines(
	SCHOOL_FULL_LINES,
	[
		_line("08.20", "Lecture hall seating & AV", "08 Joinery", parent="08", uom="No", base_qty=0.05, driver="UNITS", unit_cost=120000, trade="TRD-FIN"),
		_line("13.30", "Campus roads & landscaping", "13 External", parent="13", uom="m²", base_qty=0.25, driver="PLOT", unit_cost=480, trade="TRD-EXT"),
		_line("16.20", "Campus district cooling allowance", "16 Utilities", parent="16", uom="ls", base_qty=1, driver="FIXED", unit_cost=650000, trade="TRD-PIPE"),
	],
)

FACTORY_FULL_LINES = [
	_line("00", "Preliminaries & General", "00 Preliminaries", is_group=1),
	_line("00.10", "Industrial site establishment", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000),
	_line("00.20", "HSE & environmental compliance", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=180000),
	_line("01", "Earthworks & Platform", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Cut/fill & platform works", "01 Earthworks", parent="01", uom="m³", base_qty=0.55, driver="PLOT", unit_cost=78, trade="TRD-EARTH"),
	_line("01.20", "Subgrade compaction", "01 Earthworks", parent="01", uom="m²", base_qty=1.1, driver="PLOT", unit_cost=45, trade="TRD-EARTH"),
	_line("02", "Foundations", "02 Substructure", is_group=1, trade="TRD-SUB"),
	_line("02.10", "Pad & strip footings", "02 Substructure", parent="02", uom="m³", base_qty=0.18, driver="GFA", unit_cost=2650, trade="TRD-SUB"),
	_line("02.20", "Ground floor slab on grade", "02 Substructure", parent="02", uom="m²", base_qty=1.05, driver="GFA", unit_cost=680, trade="TRD-SUB"),
	_line("03", "Steel / PEB Structure", "03 Structure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "PEB steel supply & erection", "03 Structure", parent="03", uom="Ton", base_qty=0.085, driver="GFA", unit_cost=28500, trade="TRD-CONC"),
	_line("03.20", "Mezzanine steel (if any)", "03 Structure", parent="03", uom="Ton", base_qty=0.02, driver="FLOORS", unit_cost=26000, trade="TRD-CONC"),
	_line("05", "Cladding & Envelope", "05 Facade", is_group=1, trade="TRD-FACADE"),
	_line("05.10", "Metal cladding & louvers", "05 Facade", parent="05", uom="m²", base_qty=0.55, driver="GFA", unit_cost=980, trade="TRD-FACADE"),
	_line("07", "Industrial Flooring", "07 Finishes", is_group=1, trade="TRD-FIN"),
	_line("07.10", "Epoxy / hardener floor finish", "07 Finishes", parent="07", uom="m²", base_qty=0.95, driver="GFA", unit_cost=420, trade="TRD-FIN"),
	_line("09", "Process Plumbing", "09 MEP-P", is_group=1, trade="TRD-MEP-P"),
	_line("09.10", "Process water & drainage", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 350", unit_cost=450000, trade="TRD-MEP-P"),
	_line("10", "Ventilation & HVAC", "10 MEP-H", is_group=1, trade="TRD-MEP-H"),
	_line("10.10", "Industrial ventilation / HVAC", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 400", unit_cost=380000, trade="TRD-MEP-H"),
	_line("11", "Power & Controls", "11 MEP-E", is_group=1, trade="TRD-MEP-E"),
	_line("11.10", "MV/LV distribution & lighting", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 380", unit_cost=420000, trade="TRD-MEP-E"),
	_line("11.20", "Fire alarm & suppression", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 500", unit_cost=280000, trade="TRD-MEP-E"),
	_line("13", "External Works", "13 External", is_group=1, trade="TRD-EXT"),
	_line("13.10", "Fence, gate & external drainage", "13 External", parent="13", uom="ls", base_qty=1, driver="FIXED", unit_cost=380000, trade="TRD-EXT"),
	_line("15", "Testing & Handover", "15 Handover", is_group=1),
	_line("15.10", "Commissioning & O&M manuals", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=220000),
	_line("17", "Contingency", "17 Contingency", is_group=1),
	_line("17.10", "Provisional sum — process equipment interface", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=450000),
]

WAREHOUSE_FULL_LINES = _merge_lines(
	FACTORY_FULL_LINES,
	[
		_line("03.10", "PEB warehouse structure", "03 Structure", parent="03", uom="Ton", base_qty=0.065, driver="GFA", unit_cost=26500, trade="TRD-CONC"),
		_line("12", "Material Handling", "12 Equipment", is_group=1),
		_line("12.10", "Dock levelers & MHE allowance", "12 Equipment", parent="12", uom="No", base_qty=0.02, driver="UNITS", unit_cost=180000),
		_line("07.10", "Polished / hardstand floor", "07 Finishes", parent="07", uom="m²", base_qty=1.0, driver="GFA", unit_cost=380, trade="TRD-FIN"),
	],
	skip=frozenset({"03.10", "07.10"}),
)

BRIDGE_FULL_LINES = [
	_line("00", "Mobilization", "00 Preliminaries", is_group=1),
	_line("00.10", "Bridge site mobilization", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=520000),
	_line("00.20", "Temporary works & cofferdams", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=380000),
	_line("01", "Earthworks", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Approach embankment", "01 Earthworks", parent="01", uom="m³", base_qty=800, driver="ROAD_M", unit_cost=42, trade="TRD-EARTH"),
	_line("02", "Substructure & Piles", "02 Substructure", is_group=1, trade="TRD-SUB"),
	_line("02.10", "Bored piles / driven piles", "02 Substructure", parent="02", uom="No", base_qty=0.015, driver="ROAD_M", unit_cost=28000, trade="TRD-SUB"),
	_line("02.20", "Pile caps & abutments", "02 Substructure", parent="02", uom="m³", base_qty=120, driver="ROAD_M", unit_cost=3200, trade="TRD-SUB"),
	_line("03", "Superstructure", "03 Superstructure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "Prestressed girders / deck", "03 Superstructure", parent="03", uom="m³", base_qty=85, driver="ROAD_M", unit_cost=4800, trade="TRD-CONC"),
	_line("03.20", "Deck slab & waterproofing", "03 Superstructure", parent="03", uom="m²", base_qty=12, driver="ROAD_M", unit_cost=2200, trade="TRD-CONC"),
	_line("03.30", "Bearings & expansion joints", "03 Superstructure", parent="03", uom="No", base_qty=0.004, driver="ROAD_M", unit_cost=95000, trade="TRD-CONC"),
	_line("05", "Parapets & Finishes", "05 Facade", is_group=1, trade="TRD-FACADE"),
	_line("05.10", "Parapets & crash barriers", "05 Facade", parent="05", uom="m", base_qty=2.2, driver="ROAD_M", unit_cost=4200, trade="TRD-FACADE"),
	_line("06", "Road Furniture", "06 Furniture", is_group=1, trade="TRD-ROAD"),
	_line("06.10", "Bridge lighting & signage", "06 Furniture", parent="06", uom="ls", base_qty=1, driver="FIXED", unit_cost=280000, trade="TRD-ROAD"),
	_line("11", "Testing & Handover", "11 Handover", is_group=1),
	_line("11.10", "Load testing & as-built", "11 Handover", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=180000),
]

SUBSTATION_FULL_LINES = [
	_line("00", "Preliminaries", "00 Preliminaries", is_group=1),
	_line("00.10", "Substation mobilization", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=320000),
	_line("01", "Earthworks & Cable Trenches", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Excavation & backfill", "01 Earthworks", parent="01", uom="m³", base_qty=1200, driver="FIXED", unit_cost=95, trade="TRD-EARTH"),
	_line("01.20", "Cable trenches & ducts", "01 Earthworks", parent="01", uom="m", base_qty=850, driver="FIXED", unit_cost=2800, trade="TRD-EARTH"),
	_line("02", "Grounding & Foundations", "02 Substructure", is_group=1, trade="TRD-SUB"),
	_line("02.10", "Earthing grid & rods", "02 Substructure", parent="02", uom="ls", base_qty=1, driver="FIXED", unit_cost=680000, trade="TRD-SUB"),
	_line("03", "Civil & Control Building", "03 Structure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "Control building & foundations", "03 Structure", parent="03", uom="ls", base_qty=1, driver="FIXED", unit_cost=1450000, trade="TRD-CONC"),
	_line("11", "Primary Equipment", "11 Electrical", is_group=1, trade="TRD-MEP-E"),
	_line("11.10", "GIS / switchgear & transformers", "11 Electrical", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=3200000, trade="TRD-MEP-E"),
	_line("11.20", "Protection, SCADA & metering", "11 Electrical", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=980000, trade="TRD-MEP-E"),
	_line("11.30", "MV/LV cables & terminations", "11 Electrical", parent="11", uom="m", base_qty=2500, driver="FIXED", unit_cost=850, trade="TRD-MEP-E"),
	_line("13", "Security & Perimeter", "13 External", is_group=1, trade="TRD-EXT"),
	_line("13.10", "Fence & access control", "13 External", parent="13", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000, trade="TRD-EXT"),
	_line("17", "Contingency", "17 Contingency", is_group=1),
	_line("17.10", "Spare parts & provisional", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=280000),
	_line("15", "Commissioning", "15 Handover", is_group=1),
	_line("15.10", "Energization & testing", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000),
]

WWTP_FULL_LINES = [
	_line("00", "Preliminaries", "00 Preliminaries", is_group=1),
	_line("00.10", "WWTP mobilization", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=720000),
	_line("01", "Earthworks", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Bulk excavation for tanks", "01 Earthworks", parent="01", uom="m³", base_qty=8500, driver="FIXED", unit_cost=68, trade="TRD-EARTH"),
	_line("03", "Civil / RC Structures", "03 Structure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "Primary & secondary tanks", "03 Structure", parent="03", uom="m³", base_qty=4200, driver="FIXED", unit_cost=4200, trade="TRD-CONC"),
	_line("03.20", "Admin & blower buildings", "03 Structure", parent="03", uom="ls", base_qty=1, driver="FIXED", unit_cost=1800000, trade="TRD-CONC"),
	_line("09", "Mechanical Process", "09 MEP-P", is_group=1, trade="TRD-MEP-P"),
	_line("09.10", "Pumps, blowers & process piping", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FIXED", unit_cost=4200000, trade="TRD-MEP-P"),
	_line("09.20", "Clarifiers & sludge handling", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FIXED", unit_cost=2800000, trade="TRD-MEP-P"),
	_line("10", "Odour Control & HVAC", "10 MEP-H", is_group=1, trade="TRD-MEP-H"),
	_line("10.10", "Odour control & ventilation", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FIXED", unit_cost=950000, trade="TRD-MEP-H"),
	_line("11", "Electrical & Instrumentation", "11 MEP-E", is_group=1, trade="TRD-MEP-E"),
	_line("11.10", "MV/LV & PLC/SCADA", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=1650000, trade="TRD-MEP-E"),
	_line("13", "External Works", "13 External", is_group=1, trade="TRD-EXT"),
	_line("13.10", "Site roads & landscaping", "13 External", parent="13", uom="ls", base_qty=1, driver="FIXED", unit_cost=680000, trade="TRD-EXT"),
	_line("17", "Contingency", "17 Contingency", is_group=1),
	_line("17.10", "Process optimization allowance", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=520000),
	_line("15", "Commissioning", "15 Handover", is_group=1),
	_line("15.10", "Process performance testing", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=580000),
]

HIGHWAY_FULL_LINES = _merge_lines(
	[
		_line("00", "Mobilization", "00 Preliminaries", is_group=1),
		_line("00.10", "Highway mobilization", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=950000),
		_line("00.20", "Traffic management", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000),
		_line("01", "Earthworks", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
		_line("01.10", "Cut & fill", "01 Earthworks", parent="01", uom="m³", base_qty=1200, driver="ROAD_KM", unit_cost=18, trade="TRD-EARTH"),
		_line("01.20", "Subgrade preparation", "01 Earthworks", parent="01", uom="m³", base_qty=450, driver="ROAD_KM", unit_cost=95, trade="TRD-EARTH"),
		_line("02", "Pavement", "02 Pavement", is_group=1, trade="TRD-ROAD"),
		_line("02.10", "Sub-base & base course", "02 Pavement", parent="02", uom="Ton", base_qty=520, driver="ROAD_KM", unit_cost=380, trade="TRD-ROAD"),
		_line("02.20", "Asphalt wearing course", "02 Pavement", parent="02", uom="Ton", base_qty=850, driver="ROAD_KM", unit_cost=4200, trade="TRD-ROAD"),
		_line("03", "Structures", "03 Structures", is_group=1, trade="TRD-CONC"),
		_line("03.10", "Culverts & retaining walls", "03 Structures", parent="03", uom="ls", base_qty=1, driver="ROAD_KM", unit_cost=280000, trade="TRD-CONC"),
		_line("04", "Drainage", "04 Drainage", is_group=1, trade="TRD-PIPE"),
		_line("04.10", "Cross drainage & culverts", "04 Drainage", parent="04", uom="m", base_qty=40, driver="ROAD_KM", unit_cost=3200, trade="TRD-PIPE"),
		_line("06", "Road Furniture", "06 Furniture", is_group=1, trade="TRD-ROAD"),
		_line("06.10", "Signage, barriers & lighting", "06 Furniture", parent="06", uom="ls", base_qty=1, driver="ROAD_KM", unit_cost=180000, trade="TRD-ROAD"),
		_line("17", "Contingency", "17 Contingency", is_group=1),
		_line("17.10", "Provisional sum — traffic & safety", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=250000),
		_line("11", "Handover", "11 Handover", is_group=1),
		_line("11.10", "As-built & handover", "11 Handover", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=150000),
	],
)

URBAN_ROAD_FULL_LINES = _merge_lines(
	URBAN_ROAD_LINES,
	[
		_line("00.20", "Utility diversion allowance", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=180000),
		_line("03", "Structures", "03 Structures", is_group=1, trade="TRD-CONC"),
		_line("03.10", "Minor bridges & culverts", "03 Structures", parent="03", uom="ls", base_qty=1, driver="FORMULA", formula="ROAD_M / 2000", unit_cost=420000, trade="TRD-CONC"),
		_line("05", "Footpaths & Cycleways", "05 Footpaths", is_group=1, trade="TRD-ROAD"),
		_line("05.10", "Pedestrian paving", "05 Footpaths", parent="05", uom="m²", base_qty=1.8, driver="ROAD_M", unit_cost=420, trade="TRD-ROAD"),
		_line("07", "Street Lighting", "07 Lighting", is_group=1, trade="TRD-MEP-E"),
		_line("07.10", "Lighting poles & cabling", "07 Lighting", parent="07", uom="No", base_qty=0.08, driver="ROAD_M", unit_cost=28000, trade="TRD-MEP-E"),
	],
)


def _pipeline_full(name_ar: str, pipe_driver: str = "PIPE_KM") -> list[dict]:
	return [
		_line("00", "Mobilization", "00 Preliminaries", is_group=1),
		_line("00.10", f"Mobilization — {name_ar}", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=480000),
		_line("00.20", "Traffic & utility coordination", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=220000),
		_line("01", "Survey & Trenching", "01 Trench", is_group=1, trade="TRD-EARTH"),
		_line("01.10", "Trench excavation", "01 Trench", parent="01", uom="m", base_qty=1.1, driver=pipe_driver, unit_cost=2800, trade="TRD-EARTH"),
		_line("01.20", "Bedding & backfill", "01 Trench", parent="01", uom="m", base_qty=1.1, driver=pipe_driver, unit_cost=850, trade="TRD-EARTH"),
		_line("07", "Chambers & Valves", "07 Chambers", is_group=1, trade="TRD-PIPE"),
		_line("07.10", "Manholes / valve chambers", "07 Chambers", parent="07", uom="No", base_qty=12, driver=pipe_driver, unit_cost=42000, trade="TRD-PIPE"),
		_line("08", "Pipe Supply & Lay", "08 Pipe", is_group=1, trade="TRD-PIPE"),
		_line("08.10", "Pipe laying & jointing", "08 Pipe", parent="08", uom="m", base_qty=1.0, driver=pipe_driver, unit_cost=4200, trade="TRD-PIPE"),
		_line("08.20", "Fittings & specials", "08 Pipe", parent="08", uom="No", base_qty=8, driver=pipe_driver, unit_cost=18000, trade="TRD-PIPE"),
		_line("09", "Testing & Disinfection", "09 Test", is_group=1, trade="TRD-PIPE"),
		_line("09.10", "Pressure / leak testing", "09 Test", parent="09", uom="ls", base_qty=1, driver="FIXED", unit_cost=220000),
		_line("09.20", "Flushing & disinfection (water)", "09 Test", parent="09", uom="ls", base_qty=1, driver="FIXED", unit_cost=95000),
		_line("10", "Pumping / Stations", "10 Stations", is_group=1, trade="TRD-MEP-E"),
		_line("10.10", "Pump station civil & MEP allowance", "10 Stations", parent="10", uom="No", base_qty=0.15, driver=pipe_driver, unit_cost=850000, trade="TRD-MEP-E"),
		_line("11", "Restoration & Handover", "11 Handover", is_group=1),
		_line("11.10", "Road reinstatement & as-built", "11 Handover", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=180000),
	]


SOCIAL_HOUSING_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("03.10", "RC frame (repetitive typology T1/T2/T3)", "03 Superstructure", parent="03", uom="m³", base_qty=0.34, driver="GFA", unit_cost=2850, trade="TRD-CONC"),
		_line("07.10", "Economy unit finishes package", "07 Finishes", parent="07", uom="m²", base_qty=0.88, driver="GFA", unit_cost=720, trade="TRD-FIN"),
		_line("08.20", "Typology T1 doors & kitchen", "08 Joinery", parent="08", uom="No", base_qty=0.06, driver="UNITS", unit_cost=6200, trade="TRD-FIN"),
		_line("08.30", "Typology T2 upgrade package", "08 Joinery", parent="08", uom="No", base_qty=0.04, driver="UNITS", unit_cost=9800, trade="TRD-FIN"),
	],
	skip=frozenset({"03.10", "07.10"}),
)

HOTEL_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("08.10", "Guest room FF&E package", "08 Joinery", parent="08", uom="No", base_qty=1.2, driver="FORMULA", formula="KEY_COUNT / 50", unit_cost=45000, trade="TRD-FIN"),
		_line("10.20", "Kitchen & laundry equipment", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="KEY_COUNT / 80", unit_cost=680000, trade="TRD-MEP-H"),
		_line("11.20", "BMS / ELV hospitality", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 380", unit_cost=420000, trade="TRD-MEP-E"),
		_line("12.20", "Service lifts & dumbwaiters", "12 Lifts", parent="12", uom="No", base_qty=0.15, driver="FLOORS", unit_cost=520000),
	],
)

MALL_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("05.30", "Atrium glazing & feature facade", "05 Facade", parent="05", uom="m²", base_qty=0.08, driver="GFA", unit_cost=5200, trade="TRD-FACADE"),
		_line("12.20", "Escalators & travellators", "12 Lifts", parent="12", uom="No", base_qty=0.15, driver="FLOORS", unit_cost=420000),
		_line("08.10", "Retail fit-out allowance", "08 Joinery", parent="08", uom="m²", base_qty=0.65, driver="GFA", unit_cost=1400, trade="TRD-FIN"),
		_line("11.30", "Mall BMS & fire integration", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 350", unit_cost=480000, trade="TRD-MEP-E"),
	],
)

OFFICE_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_building_common_extras(),
	[
		_line("11.20", "Generator & UPS (office)", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 400", unit_cost=350000, trade="TRD-MEP-E"),
		_line("11.30", "Structured cabling & BMS", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 380", unit_cost=380000, trade="TRD-MEP-E"),
		_line("07.30", "Raised floor & ceiling (office)", "07 Finishes", parent="07", uom="m²", base_qty=0.85, driver="GFA", unit_cost=520, trade="TRD-FIN"),
	],
)

VILLA_FULL_LINES = _merge_lines(VILLA_LINES, _building_common_extras())

RESIDENTIAL_FULL_LINES = _merge_lines(RES_BLD_LINES, _building_common_extras())
