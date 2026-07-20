from __future__ import annotations

"""Construction material item catalog (target ~200 SKU) for procurement & BOQ BOM."""

# suffix, English, Arabic, UOM, product_type, classification
CORE_CATALOG: list[tuple[str, str, str, str, str, str]] = [
	("MAT-CEM-OPC", "Portland Cement (OPC 42.5N)", "أسمنت بورتلاند OPC", "Bag", "Raw Material", "CEM"),
	("MAT-CEM-WHITE", "White Cement", "أسمنت أبيض", "Bag", "Raw Material", "CEM"),
	("MAT-CEM-SR", "Sulfate Resistant Cement", "أسمنت مقاوم للكبريتات", "Bag", "Raw Material", "CEM"),
	("MAT-SAND-FINE", "Fine Sand (Washed)", "رمل ناعم", "m³", "Raw Material", "AGG"),
	("MAT-SAND-COARSE", "Coarse Sand", "رمل خشن", "m³", "Raw Material", "AGG"),
	("MAT-GRAVEL-10", "Crushed Gravel 10mm", "حصى 10 مم", "m³", "Raw Material", "AGG"),
	("MAT-GRAVEL-20", "Crushed Gravel 20mm", "حصى 20 مم", "m³", "Raw Material", "AGG"),
	("MAT-BASE", "Sub-base / Road Base", "طبقة أساس", "m³", "Raw Material", "AGG"),
	("MAT-STEEL-R8", "Reinforcement Steel Ø8mm", "حديد 8 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R10", "Reinforcement Steel Ø10mm", "حديد 10 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R12", "Reinforcement Steel Ø12mm", "حديد 12 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R16", "Reinforcement Steel Ø16mm", "حديد 16 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R20", "Reinforcement Steel Ø20mm", "حديد 20 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R25", "Reinforcement Steel Ø25mm", "حديد 25 مم", "Ton", "Raw Material", "STL"),
	("MAT-STEEL-R32", "Reinforcement Steel Ø32mm", "حديد 32 مم", "Ton", "Raw Material", "STL"),
	("MAT-MESH", "Welded Wire Mesh", "شبك ملحوم", "m²", "Raw Material", "STL"),
	("MAT-STRUCT-STL", "Structural Steel Sections", "حديد إنشائي", "Ton", "Raw Material", "STL"),
	("MAT-RMX-C25", "Ready-Mix Concrete C25", "خرسانة C25", "m³", "Raw Material", "CON"),
	("MAT-RMX-C30", "Ready-Mix Concrete C30/37", "خرسانة C30", "m³", "Raw Material", "CON"),
	("MAT-RMX-C40", "Ready-Mix Concrete C40/50", "خرسانة C40", "m³", "Raw Material", "CON"),
	("MAT-BLOCK", "Concrete Hollow Block", "بلك خرساني", "Nos", "Raw Material", "MAS"),
	("MAT-BRICK", "Red Clay Brick", "طوب أحمر", "Nos", "Raw Material", "MAS"),
	("MAT-TIMBER", "Formwork Timber / Ply", "خشب قوالب", "m³", "Raw Material", "FRM"),
	("MAT-WATERPROOF", "Bituminous Waterproof Membrane", "عزل bituminous", "Roll", "Raw Material", "INS"),
	("MAT-INS-FOAM", "Thermal Insulation Board", "عزل حراري", "m²", "Raw Material", "INS"),
	("MAT-PVC-50", "PVC Pipe 50mm", "PVC 50 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PVC-75", "PVC Pipe 75mm", "PVC 75 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PVC-110", "PVC Pipe 110mm", "PVC 110 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PVC-160", "PVC Pipe 160mm", "PVC 160 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PPR-20", "PPR Pipe 20mm", "PPR 20 مم", "Meter", "Raw Material", "MEP"),
	("MAT-PPR-25", "PPR Pipe 25mm", "PPR 25 مم", "Meter", "Raw Material", "MEP"),
	("MAT-COPPER-15", "Copper Pipe 15mm", "نحاس 15 مم", "Meter", "Raw Material", "MEP"),
	("MAT-COPPER-22", "Copper Pipe 22mm", "نحاس 22 مم", "Meter", "Raw Material", "MEP"),
	("MAT-CABLE-2.5", "Cable 2.5mm²", "كابل 2.5 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-4", "Cable 4mm²", "كابل 4 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-6", "Cable 6mm²", "كابل 6 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-10", "Cable 10mm²", "كابل 10 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-16", "LV Cable 4×16mm²", "كابل 16 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-25", "Power Cable 25mm²", "كابل 25 مم²", "Meter", "Raw Material", "ELE"),
	("MAT-CABLE-MV", "MV Power Cable", "كابل متوسط", "Meter", "Raw Material", "ELE"),
	("MAT-PAINT-EXT", "External Acrylic Paint", "دهان خارجي", "Liter", "Consumable", "FIN"),
	("MAT-PAINT-INT", "Internal Emulsion Paint", "دهان داخلي", "Liter", "Consumable", "FIN"),
	("MAT-TILE-30", "Floor Tile 30×30", "سيراميك 30×30", "m²", "Raw Material", "FIN"),
	("MAT-TILE-45", "Floor Tile 45×45", "سيراميك 45×45", "m²", "Raw Material", "FIN"),
	("MAT-TILE-60", "Porcelain Tile 60×60", "سيراميك 60×60", "m²", "Raw Material", "FIN"),
	("MAT-TILE-80", "Porcelain Tile 80×80", "سيراميك 80×80", "m²", "Raw Material", "FIN"),
	("MAT-GLASS-6", "Float Glass 6mm", "زجاج 6 مم", "m²", "Raw Material", "FIN"),
	("MAT-GLASS-10", "Tempered Glass 10mm", "زجاج مقسى 10 مم", "m²", "Raw Material", "FIN"),
	("MAT-ALUM", "Aluminum Curtain Wall Profile", "ألوميتال كرتن وول", "Meter", "Raw Material", "FIN"),
	("MAT-ASPHALT", "Hot Mix Asphalt (HMA)", "أسفلت ساخن", "Ton", "Raw Material", "RDW"),
	("MAT-GEOTEXT", "Geotextile Layer", "Geotextile", "m²", "Raw Material", "RDW"),
	("MAT-ADMX", "Concrete Plasticizer", "ملون خرسانة", "Liter", "Consumable", "CEM"),
	("MAT-GYPSUM", "Gypsum Board 12.5mm", "جبس بورد", "m²", "Raw Material", "FIN"),
	("MAT-DUCT", "Galvanized HVAC Duct", "مجاري تكييف", "Kg", "Raw Material", "MEP"),
	("MAT-FIRE-SEAL", "Fire Stop Sealant", "مانع حريق", "Nos", "Consumable", "SAF"),
	("MAT-DIESEL", "Diesel Fuel (Site)", "سولار", "Liter", "Consumable", "FUEL"),
	("MAT-LUBRIC", "Equipment Lubricant", "زيت تشحيم", "Liter", "Consumable", "FUEL"),
]

ITEM_PREFIX = "CONST-"

TRADE_DEFAULT_ITEMS: dict[str, list[str]] = {
	"TRD-EARTH": ["MAT-SAND-FINE", "MAT-SAND-COARSE", "MAT-BASE"],
	"TRD-SUB": ["MAT-RMX-C30", "MAT-STEEL-R16", "MAT-WATERPROOF"],
	"TRD-CONC": ["MAT-RMX-C30", "MAT-STEEL-R16", "MAT-STEEL-R12", "MAT-ADMX"],
	"TRD-FACADE": ["MAT-PAINT-EXT", "MAT-GLASS-10", "MAT-ALUM"],
	"TRD-MEP-P": ["MAT-PVC-110", "MAT-PPR-25", "MAT-COPPER-22"],
	"TRD-MEP-H": ["MAT-DUCT", "MAT-INS-FOAM"],
	"TRD-MEP-E": ["MAT-CABLE-16", "MAT-CABLE-10", "MAT-CABLE-MV"],
	"TRD-FIN": ["MAT-TILE-60", "MAT-PAINT-INT", "MAT-GYPSUM"],
	"TRD-EXT": ["MAT-SAND-FINE", "MAT-TILE-45"],
	"TRD-ROAD": ["MAT-ASPHALT", "MAT-BASE", "MAT-GEOTEXT"],
	"TRD-PIPE": ["MAT-PVC-110", "MAT-PVC-160", "MAT-PVC-75"],
}


def _generated_variants() -> list[tuple[str, str, str, str, str, str]]:
	"""Expand catalog with size/grade variants to reach ~200 items."""
	out: list[tuple[str, str, str, str, str, str]] = []
	for dia in (32, 40, 50, 63, 75, 90, 110, 125, 160, 200, 250, 315):
		s = f"MAT-HDPE-{dia}"
		out.append((s, f"HDPE Pipe {dia}mm", f"مواسير HDPE {dia} مم", "Meter", "Raw Material", "MEP"))
	for mm in (6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32):
		s = f"MAT-REBAR-{mm}"
		out.append((s, f"Rebar Ø{mm}mm", f"حديد {mm} مم", "Ton", "Raw Material", "STL"))
	for grade in ("B7", "B8", "B9", "B12", "B15", "B20", "B25", "B30", "B35", "B40"):
		s = f"MAT-CEM-{grade}"
		out.append((s, f"Cement Grade {grade}", f"أسمنت {grade}", "Bag", "Raw Material", "CEM"))
	for w in (100, 150, 200, 250, 300, 400, 500, 600, 800, 1000):
		s = f"MAT-CABLE-{w}"
		out.append((s, f"Power Cable {w}A", f"كابل {w} أمبير", "Meter", "Raw Material", "ELE"))
	for t in (20, 25, 30, 35, 40, 45, 50, 55, 60):
		s = f"MAT-RMX-C{t}"
		if any(x[0] == s for x in CORE_CATALOG + out):
			continue
		out.append((s, f"Ready-Mix C{t}", f"خرسانة C{t}", "m³", "Raw Material", "CON"))
	for h in (2.4, 2.7, 3.0, 3.6, 4.2, 4.8, 5.4, 6.0):
		s = f"MAT-BLOCK-{str(h).replace('.', '')}"
		out.append((s, f"Block {h}m height", f"بلك ارتفاع {h}", "Nos", "Raw Material", "MAS"))
	for coat in ("PRIMER", "UNDER", "TOP", "SEAL", "EPOXY"):
		s = f"MAT-COAT-{coat}"
		out.append((s, f"Coating {coat}", f"دهان {coat}", "Liter", "Consumable", "FIN"))
	for valve in ("GATE", "BALL", "CHECK", "BUTTERFLY", "GLOBE"):
		s = f"MAT-VALVE-{valve}"
		out.append((s, f"Valve {valve}", f"صمام {valve}", "Nos", "Raw Material", "MEP"))
	for pump in ("BOOST", "SUMP", "FIRE", "CIRC"):
		s = f"MAT-PUMP-{pump}"
		out.append((s, f"Pump {pump}", f"مضخة {pump}", "Nos", "Raw Material", "MEP"))
	for fix in ("ANCHOR", "BOLT-M16", "BOLT-M20", "WASHER", "NUT-M16"):
		s = f"MAT-FIX-{fix}"
		out.append((s, f"Fixing {fix}", f"مثبت {fix}", "Nos", "Raw Material", "STL"))
	for insul in ("ROCKWOOL", "XPS", "EPS", "PIR"):
		s = f"MAT-INS-{insul}"
		out.append((s, f"Insulation {insul}", f"عزل {insul}", "m²", "Raw Material", "INS"))
	for agg in ("DUST", "FILL", "LATERITE", "LIME"):
		s = f"MAT-AGG-{agg}"
		out.append((s, f"Aggregate {agg}", f"ركام {agg}", "m³", "Raw Material", "AGG"))
	return out


def full_catalog() -> list[tuple[str, str, str, str, str, str]]:
	seen: set[str] = set()
	rows: list[tuple[str, str, str, str, str, str]] = []
	for row in CORE_CATALOG + _generated_variants():
		if row[0] in seen:
			continue
		seen.add(row[0])
		rows.append(row)
	return rows[:200]


def item_code(suffix: str) -> str:
	return f"{ITEM_PREFIX}{suffix}"
