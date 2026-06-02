# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Global / international BOQ template line packs (beyond core 21 types)."""

from __future__ import annotations

from omnexa_construction.wizard.template_lines_extended import (
	HOSPITAL_FULL_LINES,
	OFFICE_FULL_LINES,
	RESIDENTIAL_FULL_LINES,
	WAREHOUSE_FULL_LINES,
	_merge_lines,
	_building_common_extras,
	_qa_ipc_extras,
)
from omnexa_construction.wizard.template_loader import RES_BLD_LINES, URBAN_ROAD_LINES, VILLA_LINES, _line


# --- Buildings & mixed-use ---
MIXED_USE_FULL_LINES = _merge_lines(
	RESIDENTIAL_FULL_LINES,
	_building_common_extras(),
	_qa_ipc_extras(),
	[
		_line("00.30", "Retail podium fit-out allowance", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 800", unit_cost=650000, trade="TRD-FIN"),
		_line("05.30", "Podium curtain wall", "05 Facade", parent="05", uom="m²", base_qty=0.18, driver="GFA", unit_cost=4200, trade="TRD-FACADE"),
		_line("12.10", "Passenger & service lifts", "12 Lifts", parent="12", uom="No", base_qty=0.012, driver="FLOORS", unit_cost=125000, trade="TRD-MEP-E"),
	],
	skip=frozenset({"17.10"}),
)

DATA_CENTER_FULL_LINES = _merge_lines(
	WAREHOUSE_FULL_LINES,
	_qa_ipc_extras(),
	[
		_line("00.20", "Tier III commissioning preliminaries", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000),
		_line("10.20", "Precision HVAC / CRAC halls", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 120", unit_cost=920000, trade="TRD-MEP-H"),
		_line("11.20", "MV switchgear, UPS & gensets", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 150", unit_cost=1100000, trade="TRD-MEP-E"),
		_line("11.30", "Structured cabling & security", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 200", unit_cost=380000, trade="TRD-MEP-E"),
	],
)

AIRPORT_TERMINAL_FULL_LINES = _merge_lines(
	OFFICE_FULL_LINES,
	_building_common_extras(),
	_qa_ipc_extras(),
	[
		_line("00.20", "Airside safety & security coordination", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=680000),
		_line("03.30", "Long-span roof steel / PT slabs", "03 Superstructure", parent="03", uom="m²", base_qty=0.55, driver="GFA", unit_cost=4200, trade="TRD-CONC"),
		_line("05.30", "Curtain wall & skylights", "05 Facade", parent="05", uom="m²", base_qty=0.48, driver="GFA", unit_cost=5200, trade="TRD-FACADE"),
		_line("07.40", "Passenger flow finishes (epoxy, stone)", "07 Finishes", parent="07", uom="m²", base_qty=0.65, driver="GFA", unit_cost=1200, trade="TRD-FIN"),
	],
)

STADIUM_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_qa_ipc_extras(),
	[
		_line("00.20", "Event safety & crowd management systems", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=520000),
		_line("03.30", "Precast seating bowl structure", "03 Superstructure", parent="03", uom="No", base_qty=0.002, driver="UNITS", unit_cost=185000, trade="TRD-CONC"),
		_line("05.20", "PT roof / cable net roof", "05 Facade", parent="05", uom="m²", base_qty=0.35, driver="GFA", unit_cost=6800, trade="TRD-FACADE"),
		_line("13.20", "Pitch / track surfacing", "13 External", parent="13", uom="m²", base_qty=0.12, driver="PLOT", unit_cost=2400, trade="TRD-EXT"),
	],
)

METRO_STATION_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_qa_ipc_extras(),
	[
		_line("00.20", "TBM / cut-and-cover logistics", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=850000),
		_line("01.30", "Deep excavation & shoring", "01 Earthworks", parent="01", uom="m³", base_qty=1.2, driver="PLOT", unit_cost=185, trade="TRD-EARTH"),
		_line("02.40", "Diaphragm walls & waterproofing", "02 Substructure", parent="02", uom="m²", base_qty=0.85, driver="PLOT", unit_cost=1200, trade="TRD-SUB"),
		_line("11.30", "Traction power & signaling interface", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=2200000, trade="TRD-MEP-E"),
	],
)

RESIDENTIAL_COMPOUND_FULL_LINES = _merge_lines(
	VILLA_LINES,
	_building_common_extras(),
	_qa_ipc_extras(),
	[
		_line("00.30", "Master infrastructure & gates", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FORMULA", formula="UNITS / 5", unit_cost=280000, trade="TRD-EXT"),
		_line("13.20", "Compound roads & lighting", "13 External", parent="13", uom="m²", base_qty=0.25, driver="PLOT", unit_cost=720, trade="TRD-EXT"),
		_line("13.30", "Landscape & irrigation", "13 External", parent="13", uom="m²", base_qty=0.4, driver="PLOT", unit_cost=380, trade="TRD-EXT"),
	],
	skip=frozenset({"00.10", "00.20"}),
)

PARKING_STRUCTURE_FULL_LINES = _merge_lines(
	RES_BLD_LINES,
	_qa_ipc_extras(),
	[
		_line("00.10", "Traffic management & phased handover", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=220000),
		_line("03.30", "Post-tensioned ramps & slabs", "03 Superstructure", parent="03", uom="m²", base_qty=0.95, driver="GFA", unit_cost=3800, trade="TRD-CONC"),
		_line("07.10", "Line marking & signage", "07 Finishes", parent="07", uom="m²", base_qty=1.0, driver="GFA", unit_cost=85, trade="TRD-FIN"),
		_line("11.20", "EV charging infrastructure", "11 MEP-E", parent="11", uom="No", base_qty=0.004, driver="GFA", unit_cost=45000, trade="TRD-MEP-E"),
	],
	skip=frozenset({"09", "10", "11", "09.10", "10.10", "11.10", "12"}),
)

LABORATORY_FULL_LINES = _merge_lines(
	HOSPITAL_FULL_LINES,
	_qa_ipc_extras(),
	[
		_line("09.30", "Lab gases & pure water systems", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 500", unit_cost=680000, trade="TRD-MEP-P"),
		_line("10.30", "Fume hood exhaust & lab HVAC", "10 MEP-H", parent="10", uom="ls", base_qty=1, driver="FORMULA", formula="GFA / 350", unit_cost=720000, trade="TRD-MEP-H"),
	],
)

# --- Infrastructure & energy ---
TUNNEL_FULL_LINES = _merge_lines(
	URBAN_ROAD_LINES,
	_qa_ipc_extras(),
	[
		_line("00.20", "TBM mobilization & grouting plant", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=1200000),
		_line("07.10", "Tunnel lining (segmental / shotcrete)", "07 Tunnel", parent="07", uom="m", base_qty=1, driver="ROAD_M", unit_cost=18500, trade="TRD-PIPE"),
		_line("08.10", "MEP tunnel services", "08 Services", parent="08", uom="m", base_qty=1, driver="ROAD_M", unit_cost=4200, trade="TRD-MEP-E"),
	],
	skip=frozenset(),
)

SOLAR_FARM_FULL_LINES = _merge_lines(
	[
		_line("00", "Preliminaries", "00 Preliminaries", is_group=1),
		_line("00.10", "Site security & access roads", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=280000, trade="TRD-EARTH"),
		_line("00.20", "Engineering & permits (grid / civil)", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=420000),
		_line("01", "Civil & Mounting", "01 Civil", is_group=1, trade="TRD-EARTH"),
		_line("01.10", "Piling & ground beams", "01 Civil", parent="01", uom="No", base_qty=0.02, driver="PLOT", unit_cost=12000, trade="TRD-SUB"),
		_line("01.20", "Tracker / fixed mounting structures", "01 Civil", parent="01", uom="MW", base_qty=1, driver="FIXED", unit_cost=420000, trade="TRD-CONC"),
		_line("01.30", "Fencing & site drainage", "01 Civil", parent="01", uom="ls", base_qty=1, driver="FIXED", unit_cost=185000, trade="TRD-EXT"),
		_line("11", "Electrical & Grid", "11 Electrical", is_group=1, trade="TRD-MEP-E"),
		_line("11.10", "PV modules & DC cabling", "11 Electrical", parent="11", uom="MW", base_qty=1, driver="FIXED", unit_cost=680000, trade="TRD-MEP-E"),
		_line("11.20", "Inverters & MV substation", "11 Electrical", parent="11", uom="MW", base_qty=1, driver="FIXED", unit_cost=320000, trade="TRD-MEP-E"),
		_line("11.30", "SCADA & performance monitoring", "11 Electrical", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=240000, trade="TRD-MEP-E"),
		_line("13", "External Works", "13 External", is_group=1, trade="TRD-EXT"),
		_line("13.10", "O&M building & hardstanding", "13 External", parent="13", uom="ls", base_qty=1, driver="FIXED", unit_cost=320000, trade="TRD-EXT"),
		_line("15", "Testing & Grid connection", "15 Handover", is_group=1),
		_line("15.10", "Commissioning & performance test", "15 Handover", parent="15", uom="ls", base_qty=1, driver="FIXED", unit_cost=180000),
		_line("17", "Contingency", "17 Contingency", is_group=1),
		_line("17.10", "Design & weather contingency", "17 Contingency", parent="17", uom="ls", base_qty=1, driver="FIXED", unit_cost=250000),
	],
	_qa_ipc_extras(),
)

POWER_PLANT_FULL_LINES = _merge_lines(
	WAREHOUSE_FULL_LINES,
	_qa_ipc_extras(),
	[
		_line("03.30", "Turbine hall steel structure", "03 Structure", parent="03", uom="Ton", base_qty=0.12, driver="GFA", unit_cost=42000, trade="TRD-CONC"),
		_line("09.20", "Steam / water cycle piping", "09 MEP-P", parent="09", uom="ls", base_qty=1, driver="FIXED", unit_cost=4200000, trade="TRD-MEP-P"),
		_line("11.30", "Generator step-up & switchyard", "11 MEP-E", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=5800000, trade="TRD-MEP-E"),
	],
)

RAILWAY_FULL_LINES = _merge_lines(
	URBAN_ROAD_LINES,
	_qa_ipc_extras(),
	[
		_line("00.20", "Rail possession & safety (PTW)", "00 Preliminaries", parent="00", uom="ls", base_qty=1, driver="FIXED", unit_cost=380000),
		_line("03.10", "Track bed & ballast", "03 Track", parent="03", uom="m", base_qty=1, driver="ROAD_M", unit_cost=2800, trade="TRD-ROAD"),
		_line("03.20", "Rails, sleepers & fasteners", "03 Track", parent="03", uom="m", base_qty=1, driver="ROAD_M", unit_cost=4200, trade="TRD-ROAD"),
		_line("06.10", "Platforms & canopies", "06 Stations", parent="06", uom="No", base_qty=0.001, driver="ROAD_M", unit_cost=850000, trade="TRD-CONC"),
		_line("11.10", "Traction power & signaling", "11 Electrical", parent="11", uom="ls", base_qty=1, driver="FIXED", unit_cost=2400000, trade="TRD-MEP-E"),
	],
)

DISTRICT_COOLING_FULL_LINES = _merge_lines(
	URBAN_ROAD_LINES,
	_qa_ipc_extras(),
	[
		_line("08.10", "Chilled water mains", "08 Distribution", parent="08", uom="km", base_qty=1, driver="PIPE_KM", unit_cost=2800000, trade="TRD-PIPE"),
		_line("08.20", "Energy transfer stations (ETS)", "08 Distribution", parent="08", uom="No", base_qty=0.5, driver="PIPE_KM", unit_cost=1800000, trade="TRD-MEP-H"),
		_line("10.10", "Central chiller plant", "10 Plant", parent="10", uom="ls", base_qty=1, driver="FIXED", unit_cost=8500000, trade="TRD-MEP-H"),
	],
)
