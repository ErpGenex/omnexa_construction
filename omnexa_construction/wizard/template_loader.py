from __future__ import annotations

"""Seed data for Construction BOQ templates and trade packages (Phase 4 MVP)."""

TRADE_PACKAGES: list[dict] = [
	{"trade_code": "TRD-EARTH", "trade_name": "Earthworks & Site", "trade_name_ar": "ترابيات وموقع", "boq_section_prefixes": "01", "default_retention_percent": 5
	},
	{"trade_code": "TRD-SUB", "trade_name": "Substructure / Piling", "trade_name_ar": "أساسات", "boq_section_prefixes": "02", "default_retention_percent": 5
	},
	{"trade_code": "TRD-CONC", "trade_name": "Concrete & Structure", "trade_name_ar": "خرسانة وهيكل", "boq_section_prefixes": "03", "default_retention_percent": 5
	},
	{"trade_code": "TRD-FACADE", "trade_name": "Facade & Envelope", "trade_name_ar": "واجهات", "boq_section_prefixes": "05", "default_retention_percent": 5
	},
	{"trade_code": "TRD-MEP-P", "trade_name": "Plumbing & Drainage", "trade_name_ar": "سباكة وصرف", "boq_section_prefixes": "09", "default_retention_percent": 5
	},
	{"trade_code": "TRD-MEP-H", "trade_name": "HVAC", "trade_name_ar": "تكييف", "boq_section_prefixes": "10", "default_retention_percent": 5
	},
	{"trade_code": "TRD-MEP-E", "trade_name": "Electrical & ELV", "trade_name_ar": "كهرباء", "boq_section_prefixes": "11", "default_retention_percent": 5
	},
	{"trade_code": "TRD-FIN", "trade_name": "Finishes & Joinery", "trade_name_ar": "تشطيبات", "boq_section_prefixes": "07,08", "default_retention_percent": 5
	},
	{"trade_code": "TRD-EXT", "trade_name": "External Works", "trade_name_ar": "أعمال خارجية", "boq_section_prefixes": "13,14", "default_retention_percent": 5
	},
	{"trade_code": "TRD-ROAD", "trade_name": "Roads & Pavement", "trade_name_ar": "طرق ورصف", "boq_section_prefixes": "02,03", "default_retention_percent": 5
	},
	{"trade_code": "TRD-PIPE", "trade_name": "Pipeline Installation", "trade_name_ar": "شبكات", "boq_section_prefixes": "07,08", "default_retention_percent": 5
	},
]

def _line(
	cost_code: str,
	desc: str,
	section: str,
	*,
	parent: str = "",
	is_group: int = 0,
	uom: str = "Nos",
	base_qty: float = 1,
	driver: str = "FIXED",
	formula: str = "",
	unit_cost: float = 0,
	labor: float = 40,
	material: float = 50,
	equipment: float = 10,
	trade: str = "",
) -> dict:
	return {
		"section_name": section,
		"cost_code": cost_code,
		"item_description": desc,
		"parent_cost_code": parent,
		"is_group": is_group,
		"unit_of_measure": uom,
		"base_quantity": base_qty,
		"quantity_driver": driver,
		"driver_formula": formula,
		"unit_cost_base": unit_cost,
		"labor_ratio": labor,
		"material_ratio": material,
		"equipment_ratio": equipment,
		"trade_package_code": trade
	}


VILLA_LINES = [
	_line("00", "Preliminaries & General Requirements", "00 Preliminaries", is_group=1),
	_line("00.10", "Site setup, hoarding, safety", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=85000, trade="TRD-EARTH"),
	_line("00.20", "Project insurance & bonds (allowance)", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=120000),
	_line("01", "Earthworks & Site Preparation", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Bulk excavation & disposal", "01 Earthworks", parent="01", uom="m³", base_qty=0.8, driver="PLOT", unit_cost=95, trade="TRD-EARTH"),
	_line("01.20", "Backfill & compaction", "01 Earthworks", parent="01", uom="m³", base_qty=0.35, driver="PLOT", unit_cost=75, trade="TRD-EARTH"),
	_line("02", "Substructure", "02 Substructure", is_group=1, trade="TRD-SUB"),
	_line("02.10", "Raft foundation concrete C30", "02 Substructure", parent="02", uom="m³", base_qty=0.28, driver="GFA", unit_cost=2800, trade="TRD-SUB"),
	_line("02.20", "Foundation reinforcement", "02 Substructure", parent="02", uom="Ton", base_qty=0.085, driver="GFA", unit_cost=32000, trade="TRD-SUB"),
	_line("02.30", "Waterproofing to basement/raft", "02 Substructure", parent="02", uom="m²", base_qty=1.05, driver="PLOT", unit_cost=420, trade="TRD-SUB"),
	_line("03", "Superstructure", "03 Superstructure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "RC columns, beams, slabs", "03 Superstructure", parent="03", uom="m³", base_qty=0.42, driver="GFA", unit_cost=3100, trade="TRD-CONC"),
	_line("03.20", "Blockwork infill", "03 Superstructure", parent="03", uom="m²", base_qty=0.55, driver="GFA", unit_cost=380, trade="TRD-CONC"),
	_line("05", "External Envelope", "05 Facade", is_group=1, trade="TRD-FACADE"),
	_line("05.10", "External paint system", "05 Facade", parent="05", uom="m²", base_qty=0.45, driver="GFA", unit_cost=220, trade="TRD-FACADE"),
	_line("05.20", "Aluminum windows & doors", "05 Facade", parent="05", uom="m²", base_qty=0.22, driver="GFA", unit_cost=4200, trade="TRD-FACADE"),
	_line("09", "Plumbing & Drainage", "09 MEP-P", is_group=1, trade="TRD-MEP-P"),
	_line("09.10", "Complete plumbing installation", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 350", unit_cost=450000, trade="TRD-MEP-P"),
	_line("10", "HVAC", "10 MEP-H", is_group=1, trade="TRD-MEP-H"),
	_line("10.10", "Split units + ducting allowance", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 400", unit_cost=380000, trade="TRD-MEP-H"),
	_line("11", "Electrical & ELV", "11 MEP-E", is_group=1, trade="TRD-MEP-E"),
	_line("11.10", "Complete electrical installation", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 380", unit_cost=420000, trade="TRD-MEP-E"),
	_line("07", "Finishes", "07 Finishes", is_group=1, trade="TRD-FIN"),
	_line("07.10", "Floor finishes (porcelain)", "07 Finishes", parent="07", uom="m²", base_qty=1.0, driver="GFA", unit_cost=850, trade="TRD-FIN"),
	_line("07.20", "Internal wall paint", "07 Finishes", parent="07", uom="m²", base_qty=2.8, driver="GFA", unit_cost=120, trade="TRD-FIN"),
	_line("07.30", "Ceiling gypsum", "07 Finishes", parent="07", uom="m²", base_qty=1.0, driver="GFA", unit_cost=420, trade="TRD-FIN"),
	_line("13", "External Works", "13 External", is_group=1, trade="TRD-EXT"),
	_line("13.10", "Landscape soft & hardscape", "13 External", parent="13", uom="m²", base_qty=0.35, driver="PLOT", unit_cost=650, trade="TRD-EXT"),
	_line("15", "Testing & Handover", "15 Handover", is_group=1),
	_line("15.10", "Testing, commissioning, O&M manuals", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=95000),
]

RES_BLD_LINES = [
	_line("00", "Preliminaries", "00 Preliminaries", is_group=1),
	_line("00.10", "Site establishment & tower crane", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=450000),
	_line("01", "Earthworks", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Excavation for basements", "01 Earthworks", parent="01", uom="m³", base_qty=0.9, driver="PLOT", unit_cost=110, trade="TRD-EARTH"),
	_line("02", "Substructure & Piles", "02 Substructure", is_group=1, trade="TRD-SUB"),
	_line("02.10", "Piled foundation (allowance)", "02 Substructure", parent="02", uom="No", base_qty=0.08, driver="GFA", unit_cost=8500, trade="TRD-SUB"),
	_line("02.20", "Raft & retaining walls", "02 Substructure", parent="02", uom="m³", base_qty=0.32, driver="GFA", unit_cost=2950, trade="TRD-SUB"),
	_line("03", "Superstructure", "03 Superstructure", is_group=1, trade="TRD-CONC"),
	_line("03.10", "RC frame per floor cycle", "03 Superstructure", parent="03", uom="m³", base_qty=0.38, driver="GFA", unit_cost=3050, trade="TRD-CONC"),
	_line("03.20", "Precast stairs & landings", "03 Superstructure", parent="03", uom="No", base_qty=0.015, driver="FLOORS", unit_cost=85000, trade="TRD-CONC"),
	_line("05", "Facade & Envelope", "05 Facade", is_group=1, trade="TRD-FACADE"),
	_line("05.10", "Curtain wall / cladding", "05 Facade", parent="05", uom="m²", base_qty=0.52, driver="GFA", unit_cost=3800, trade="TRD-FACADE"),
	_line("12", "Lifts", "12 Lifts", is_group=1),
	_line("12.10", "Passenger lifts (supply & install)", "12 Lifts", parent="12", uom="No", base_qty=0.25, driver="FLOORS", unit_cost=650000),
	_line("09", "Plumbing", "09 MEP-P", is_group=1, trade="TRD-MEP-P"),
	_line("09.10", "Risers & apartment plumbing", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 280", unit_cost=520000, trade="TRD-MEP-P"),
	_line("10", "HVAC", "10 MEP-H", is_group=1, trade="TRD-MEP-H"),
	_line("10.10", "Central HVAC / splits mix", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 320", unit_cost=480000, trade="TRD-MEP-H"),
	_line("11", "Electrical", "11 MEP-E", is_group=1, trade="TRD-MEP-E"),
	_line("11.10", "MV/LV + apartment metering", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 300", unit_cost=550000, trade="TRD-MEP-E"),
	_line("07", "Finishes", "07 Finishes", is_group=1, trade="TRD-FIN"),
	_line("07.10", "Typical apartment finishes", "07 Finishes", parent="07", uom="m²", base_qty=0.92, driver="GFA", unit_cost=1100, trade="TRD-FIN"),
	_line("07.20", "Common area finishes", "07 Finishes", parent="07", uom="m²", base_qty=0.18, driver="GFA", unit_cost=950, trade="TRD-FIN"),
	_line("13", "External works", "13 External", is_group=1, trade="TRD-EXT"),
	_line("13.10", "Podium landscape & parking", "13 External", parent="13", uom="m²", base_qty=0.25, driver="PLOT", unit_cost=780, trade="TRD-EXT"),
]

URBAN_ROAD_LINES = [
	_line("00", "Mobilization", "00 Preliminaries", is_group=1),
	_line("00.10", "Traffic management & mobilization", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=320000),
	_line("01", "Earthworks & Subgrade", "01 Earthworks", is_group=1, trade="TRD-EARTH"),
	_line("01.10", "Excavation & subgrade preparation", "01 Earthworks", parent="01", uom="m³", base_qty=1.2, driver="ROAD_M", unit_cost=85, trade="TRD-EARTH"),
	_line("01.20", "Sub-base layer", "01 Earthworks", parent="01", uom="m³", base_qty=0.45, driver="ROAD_M", unit_cost=420, trade="TRD-EARTH"),
	_line("02", "Pavement Structure", "02 Pavement", is_group=1, trade="TRD-ROAD"),
	_line("02.10", "Asphalt wearing course", "02 Pavement", parent="02", uom="Ton", base_qty=0.028, driver="ROAD_M", unit_cost=4200, trade="TRD-ROAD"),
	_line("02.20", "Kerb & channel", "02 Pavement", parent="02", uom="m", base_qty=2.0, driver="ROAD_M", unit_cost=650, trade="TRD-ROAD"),
	_line("04", "Drainage", "04 Drainage", is_group=1, trade="TRD-PIPE"),
	_line("04.10", "Storm water pipes & manholes", "04 Drainage", parent="04", uom="m", base_qty=0.85, driver="ROAD_M", unit_cost=2800, trade="TRD-PIPE"),
	_line("06", "Road Furniture", "06 Furniture", is_group=1, trade="TRD-ROAD"),
	_line("06.10", "Signage & road marking", "06 Furniture", parent="06", uom="ls", base_qty=1, driver="FORMULA", formula="ROAD_M / 500", unit_cost=180000, trade="TRD-ROAD"),
	_line("11", "Commissioning", "11 Handover", is_group=1),
	_line("11.10", "As-built survey & handover", "11 Handover", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=65000),
]

