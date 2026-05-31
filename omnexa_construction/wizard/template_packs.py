from __future__ import annotations

"""Full template packs: BOQ lines + default phases + detail specs per project type."""

from omnexa_construction.wizard.template_loader import (
	_line,
	RES_BLD_LINES,
	URBAN_ROAD_LINES,
	VILLA_LINES,
)
from omnexa_construction.wizard.template_lines_extended import (
	BRIDGE_FULL_LINES,
	FACTORY_FULL_LINES,
	HIGHWAY_FULL_LINES,
	HOSPITAL_FULL_LINES,
	HOTEL_FULL_LINES,
	MALL_FULL_LINES,
	OFFICE_FULL_LINES,
	RESIDENTIAL_FULL_LINES,
	SCHOOL_FULL_LINES,
	SOCIAL_HOUSING_FULL_LINES,
	SUBSTATION_FULL_LINES,
	UNIVERSITY_FULL_LINES,
	URBAN_ROAD_FULL_LINES,
	VILLA_FULL_LINES,
	WAREHOUSE_FULL_LINES,
	WWTP_FULL_LINES,
	_pipeline_full,
)

# Phase presets: (code, name_en, name_ar, prefixes, weight%, months_from_start, months_duration)
PHASE_BUILDING_STD = [
	("P1", "Substructure & Earthworks", "الأعمال الترابية والأساسات", "00,01,02", 22, 0, 4),
	("P2", "Structure & Envelope", "الهيكل والواجهات", "03,04,05,06", 33, 4, 6),
	("P3", "MEP Systems", "الأنظمة الميكانيكية والكهربائية", "09,10,11,12", 28, 10, 5),
	("P4", "Finishes & Handover", "التشطيبات والتسليم", "07,08,13,14,15,16", 17, 15, 3),
]

PHASE_COMMERCIAL = [
	("P1", "Site & Substructure", "الموقع والأساسات", "00,01,02", 18, 0, 5),
	("P2", "Core & Shell", "الهيكل والواجهة", "03,04,05,06,12", 38, 5, 8),
	("P3", "MEP & Vertical", "الأنظمة والمصاعد", "09,10,11,12", 27, 13, 6),
	("P4", "Fit-out & Opening", "التشطيبات والافتتاح", "07,08,13,15", 17, 19, 4),
]

PHASE_HEALTHCARE = [
	("P1", "Site & Substructure", "الموقع والأساسات", "00,01,02", 20, 0, 6),
	("P2", "Structure & Shell", "الهيكل", "03,04,05", 32, 6, 8),
	("P3", "MEP & Medical Gases", "الأنظمة والغازات الطبية", "09,10,11", 30, 14, 7),
	("P4", "Finishes & Commissioning", "التشطيبات والتشغيل", "07,08,13,15", 18, 21, 5),
]

PHASE_EDUCATION = [
	("P1", "Site & Structure", "الموقع والهيكل", "00,01,02,03", 40, 0, 8),
	("P2", "Envelope & Roof", "الواجهات والأسقف", "04,05,06", 20, 8, 4),
	("P3", "MEP", "الأنظمة", "09,10,11", 25, 12, 5),
	("P4", "Finishes & Handover", "التشطيبات", "07,08,13,15", 15, 17, 3),
]

PHASE_INDUSTRIAL = [
	("P1", "Site & Foundations", "الموقع والأساسات", "00,01,02", 25, 0, 3),
	("P2", "Steel / Structure", "الهيكل المعدني/الخرساني", "03,04", 40, 3, 5),
	("P3", "MEP & Process", "الأنظمة والعمليات", "09,10,11,16", 25, 8, 4),
	("P4", "Testing & Handover", "الاختبار والتسليم", "13,15", 10, 12, 2),
]

PHASE_ROAD = [
	("P1", "Mobilization & Earthworks", "التجهيز والترابيات", "00,01", 30, 0, 3),
	("P2", "Pavement & Structures", "الرصف والمنشآت", "02,03,05", 45, 3, 5),
	("P3", "Drainage & Utilities", "الصرف والمرافق", "04,07", 15, 8, 3),
	("P4", "Furniture & Handover", "الأثاث والتسليم", "06,11", 10, 11, 2),
]

PHASE_PIPELINE = [
	("P1", "Survey & Trenching", "المسح والحفريات", "00,01,07", 25, 0, 4),
	("P2", "Pipe Laying", "تركيب المواسير", "08", 45, 4, 6),
	("P3", "Testing & Chambers", "الاختبار والغرف", "09,10", 20, 10, 3),
	("P4", "Commissioning", "التشغيل والتسليم", "11", 10, 13, 2),
]

# Default detail breakdown per cost-code suffix (applied to matching leaf lines)
DETAIL_RULES_DEFAULT = [
	{"suffix": ".10", "specs": [
		("Labor / installation", 0.45, 0.35, 0.20),
		("Materials supply", 0.15, 0.75, 0.10),
	]},
	{"suffix": ".20", "specs": [
		("Labor", 0.40, 0.45, 0.15),
		("Materials", 0.10, 0.80, 0.10),
	]},
]

DETAIL_RULES_MEP_LS = [
	{"suffix": ".10", "specs": [
		("Design & engineering", 0.25, 0.05, 0.70),
		("Installation labor", 0.55, 0.25, 0.20),
		("Materials & equipment", 0.10, 0.65, 0.25),
	]},
]


def _pipeline_lines(name_ar: str, pipe_driver: str = "PIPE_KM"):
	return _pipeline_full(name_ar, pipe_driver)


# Legacy helpers kept for imports/tests
def _hotel_lines():
	return HOTEL_FULL_LINES


def _mall_lines():
	return MALL_FULL_LINES


def _hospital_lines():
	return HOSPITAL_FULL_LINES


def _school_lines():
	return SCHOOL_FULL_LINES


def _highway_lines():
	return HIGHWAY_FULL_LINES


def _office_lines():
	return OFFICE_FULL_LINES


def _social_housing_lines():
	return SOCIAL_HOUSING_FULL_LINES


def _factory_lines():
	return FACTORY_FULL_LINES


def _warehouse_lines():
	return WAREHOUSE_FULL_LINES


def _university_lines():
	return UNIVERSITY_FULL_LINES


BUILDING_TYPE_META: dict[str, dict] = {
	"villa": {"segment": "Buildings", "template_code": "VILLA-TURNKEY-STD", "label_en": "Villa", "label_ar": "فيلا"},
	"residential_building": {"segment": "Buildings", "template_code": "RES-BLD-TURNKEY-STD", "label_en": "Residential Building", "label_ar": "عمارة سكنية"},
	"social_housing": {"segment": "Buildings", "template_code": "SOCIAL-HOUSING-UP", "label_en": "Social Housing", "label_ar": "إسكان اجتماعي"},
	"office_tower": {"segment": "Buildings", "template_code": "OFFICE-TOWER-STD", "label_en": "Office Tower", "label_ar": "برج إداري"},
	"hotel": {"segment": "Buildings", "template_code": "HOTEL-TURNKEY-STD", "label_en": "Hotel", "label_ar": "فندق"},
	"mall": {"segment": "Buildings", "template_code": "MALL-TURNKEY-STD", "label_en": "Shopping Mall", "label_ar": "مول تجاري"},
	"school": {"segment": "Buildings", "template_code": "SCHOOL-TURNKEY-STD", "label_en": "School", "label_ar": "مدرسة"},
	"hospital": {"segment": "Buildings", "template_code": "HOSPITAL-EPC-STD", "label_en": "Hospital", "label_ar": "مستشفى"},
	"university": {"segment": "Buildings", "template_code": "UNIVERSITY-PHASE-STD", "label_en": "University", "label_ar": "حرم جامعي"},
	"warehouse": {"segment": "Industrial EPC", "template_code": "WAREHOUSE-STD", "label_en": "Warehouse", "label_ar": "مخزن"},
	"factory": {"segment": "Industrial EPC", "template_code": "FACTORY-EPC-STD", "label_en": "Factory", "label_ar": "مصنع"},
	"highway": {"segment": "Roads & Utilities", "template_code": "HIGHWAY-UP-STD", "label_en": "Highway", "label_ar": "طريق سريع"},
	"urban_road": {"segment": "Roads & Utilities", "template_code": "URBAN-ROAD-STD", "label_en": "Urban Road", "label_ar": "طريق حضري"},
	"bridge": {"segment": "Infrastructure", "template_code": "BRIDGE-STD", "label_en": "Bridge", "label_ar": "كوبري"},
	"water_network": {"segment": "Roads & Utilities", "template_code": "WATER-NET-STD", "label_en": "Water Network", "label_ar": "شبكة مياه"},
	"sewer_network": {"segment": "Roads & Utilities", "template_code": "SEWER-NET-STD", "label_en": "Sewer Network", "label_ar": "شبكة صرف"},
	"electrical_network": {"segment": "Roads & Utilities", "template_code": "ELEC-NET-STD", "label_en": "Electrical Network", "label_ar": "شبكة كهرباء"},
	"gas_network": {"segment": "Roads & Utilities", "template_code": "GAS-NET-STD", "label_en": "Gas Network", "label_ar": "شبكة غاز"},
	"telecom_fiber": {"segment": "Roads & Utilities", "template_code": "TELECOM-FIBER-STD", "label_en": "Telecom / Fiber", "label_ar": "شبكة فايبر"},
	"substation": {"segment": "Industrial EPC", "template_code": "SUBSTATION-EPC", "label_en": "Substation", "label_ar": "محطة كهرباء"},
	"wastewater_plant": {"segment": "Infrastructure", "template_code": "WWTP-TURNKEY", "label_en": "WWTP", "label_ar": "محطة معالجة"},
}


TEMPLATE_PACKS: dict[str, dict] = {}


def _register(code: str, meta: dict, lines: list, phases: list, detail_rules=None, duration_months: int = 18):
	TEMPLATE_PACKS[code] = {
		**meta,
		"lines": lines,
		"phases": phases,
		"detail_rules": detail_rules or DETAIL_RULES_DEFAULT,
		"duration_months": duration_months,
	}


_register(
	"VILLA-TURNKEY-STD",
	{"template_code": "VILLA-TURNKEY-STD", "template_name": "Villa Turnkey", "template_name_ar": "فيلا تسليم مفتاح", "building_type": "villa", "project_segment": "Buildings", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Silver Book (EPC/Turnkey)", "quality_tier": "Standard"},
	VILLA_FULL_LINES,
	PHASE_BUILDING_STD,
	duration_months=14,
)
_register(
	"RES-BLD-TURNKEY-STD",
	{"template_code": "RES-BLD-TURNKEY-STD", "template_name": "Residential Building", "template_name_ar": "عمارة سكنية", "building_type": "residential_building", "project_segment": "Buildings", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	RESIDENTIAL_FULL_LINES,
	PHASE_BUILDING_STD,
	duration_months=20,
)
_register(
	"HOTEL-TURNKEY-STD",
	{"template_code": "HOTEL-TURNKEY-STD", "template_name": "Hotel Turnkey", "template_name_ar": "فندق تسليم مفتاح", "building_type": "hotel", "project_segment": "Buildings", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Silver Book (EPC/Turnkey)", "quality_tier": "Premium"},
	_hotel_lines(),
	PHASE_COMMERCIAL,
	DETAIL_RULES_MEP_LS,
	24,
)
_register(
	"MALL-TURNKEY-STD",
	{"template_code": "MALL-TURNKEY-STD", "template_name": "Shopping Mall", "template_name_ar": "مول تجاري", "building_type": "mall", "project_segment": "Buildings", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Premium"},
	_mall_lines(),
	PHASE_COMMERCIAL,
	duration_months=28,
)
_register(
	"HOSPITAL-EPC-STD",
	{"template_code": "HOSPITAL-EPC-STD", "template_name": "Hospital EPC", "template_name_ar": "مستشفى تسليم مفتاح", "building_type": "hospital", "project_segment": "Buildings", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Silver Book (EPC/Turnkey)", "quality_tier": "Premium"},
	_hospital_lines(),
	PHASE_HEALTHCARE,
	DETAIL_RULES_MEP_LS,
	30,
)
_register(
	"SCHOOL-TURNKEY-STD",
	{"template_code": "SCHOOL-TURNKEY-STD", "template_name": "School", "template_name_ar": "مدرسة", "building_type": "school", "project_segment": "Buildings", "default_contract_type": "Lump Sum", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_school_lines(),
	PHASE_EDUCATION,
	duration_months=16,
)
_register(
	"UNIVERSITY-PHASE-STD",
	{"template_code": "UNIVERSITY-PHASE-STD", "template_name": "University Campus", "template_name_ar": "حرم جامعي", "building_type": "university", "project_segment": "Buildings", "default_contract_type": "Lump Sum", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_university_lines(),
	PHASE_EDUCATION,
	duration_months=24,
)
_register(
	"OFFICE-TOWER-STD",
	{"template_code": "OFFICE-TOWER-STD", "template_name": "Office Tower", "template_name_ar": "برج إداري", "building_type": "office_tower", "project_segment": "Buildings", "default_contract_type": "Lump Sum", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Premium"},
	_office_lines(),
	PHASE_COMMERCIAL,
	duration_months=22,
)
_register(
	"SOCIAL-HOUSING-UP",
	{"template_code": "SOCIAL-HOUSING-UP", "template_name": "Social Housing", "template_name_ar": "إسكان اجتماعي", "building_type": "social_housing", "project_segment": "Buildings", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Economy"},
	_social_housing_lines(),
	PHASE_BUILDING_STD,
	duration_months=22,
)
_register(
	"WAREHOUSE-STD",
	{"template_code": "WAREHOUSE-STD", "template_name": "Warehouse", "template_name_ar": "مخزن", "building_type": "warehouse", "project_segment": "Industrial EPC", "default_contract_type": "Lump Sum", "default_governing_standard": "FIDIC 2017 Yellow Book", "quality_tier": "Standard"},
	_warehouse_lines(),
	PHASE_INDUSTRIAL,
	duration_months=10,
)
_register(
	"FACTORY-EPC-STD",
	{"template_code": "FACTORY-EPC-STD", "template_name": "Factory EPC", "template_name_ar": "مصنع", "building_type": "factory", "project_segment": "Industrial EPC", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Yellow Book", "quality_tier": "Standard"},
	_factory_lines(),
	PHASE_INDUSTRIAL,
	duration_months=14,
)
_register(
	"URBAN-ROAD-STD",
	{"template_code": "URBAN-ROAD-STD", "template_name": "Urban Road", "template_name_ar": "طريق حضري", "building_type": "urban_road", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	URBAN_ROAD_FULL_LINES,
	PHASE_ROAD,
	duration_months=8,
)
_register(
	"HIGHWAY-UP-STD",
	{"template_code": "HIGHWAY-UP-STD", "template_name": "Highway", "template_name_ar": "طريق سريع", "building_type": "highway", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_highway_lines(),
	PHASE_ROAD,
	duration_months=18,
)
_register(
	"WATER-NET-STD",
	{"template_code": "WATER-NET-STD", "template_name": "Water Network", "template_name_ar": "شبكة مياه", "building_type": "water_network", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_pipeline_lines("شبكة مياه"),
	PHASE_PIPELINE,
	duration_months=12,
)
_register(
	"SEWER-NET-STD",
	{"template_code": "SEWER-NET-STD", "template_name": "Sewer Network", "template_name_ar": "شبكة صرف", "building_type": "sewer_network", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_pipeline_lines("شبكة صرف"),
	PHASE_PIPELINE,
	duration_months=12,
)
_register(
	"ELEC-NET-STD",
	{"template_code": "ELEC-NET-STD", "template_name": "Electrical Network", "template_name_ar": "شبكة كهرباء", "building_type": "electrical_network", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_pipeline_lines("شبكة كهرباء", "ROAD_KM"),
	PHASE_PIPELINE,
	duration_months=14,
)
_register(
	"GAS-NET-STD",
	{"template_code": "GAS-NET-STD", "template_name": "Gas Network", "template_name_ar": "شبكة غاز", "building_type": "gas_network", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_pipeline_lines("شبكة غاز"),
	PHASE_PIPELINE,
	duration_months=10,
)
_register(
	"TELECOM-FIBER-STD",
	{"template_code": "TELECOM-FIBER-STD", "template_name": "Telecom Fiber", "template_name_ar": "فايبر", "building_type": "telecom_fiber", "project_segment": "Roads & Utilities", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	_pipeline_lines("اتصالات", "PIPE_KM"),
	PHASE_PIPELINE,
	duration_months=8,
)
_register(
	"BRIDGE-STD",
	{"template_code": "BRIDGE-STD", "template_name": "Bridge / Viaduct", "template_name_ar": "كوبري", "building_type": "bridge", "project_segment": "Infrastructure", "default_contract_type": "Unit Price", "default_governing_standard": "FIDIC 2017 Red Book", "quality_tier": "Standard"},
	BRIDGE_FULL_LINES,
	PHASE_ROAD,
	duration_months=16,
)
_register(
	"SUBSTATION-EPC",
	{"template_code": "SUBSTATION-EPC", "template_name": "Substation EPC", "template_name_ar": "محطة كهرباء", "building_type": "substation", "project_segment": "Industrial EPC", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Yellow Book", "quality_tier": "Standard"},
	SUBSTATION_FULL_LINES,
	PHASE_INDUSTRIAL,
	DETAIL_RULES_MEP_LS,
	12,
)
_register(
	"WWTP-TURNKEY",
	{"template_code": "WWTP-TURNKEY", "template_name": "WWTP Turnkey", "template_name_ar": "محطة معالجة", "building_type": "wastewater_plant", "project_segment": "Infrastructure", "default_contract_type": "Turnkey (EPC)", "default_governing_standard": "FIDIC 2017 Silver Book (EPC/Turnkey)", "quality_tier": "Standard"},
	WWTP_FULL_LINES,
	PHASE_INDUSTRIAL,
	DETAIL_RULES_MEP_LS,
	20,
)

# Backward-compatible export for template_loader import
BOQ_TEMPLATES = [
	{
		"template_code": k,
		"template_name": v["template_name"],
		"template_name_ar": v["template_name_ar"],
		"building_type": v["building_type"],
		"project_segment": v["project_segment"],
		"default_contract_type": v["default_contract_type"],
		"default_governing_standard": v["default_governing_standard"],
		"quality_tier": v["quality_tier"],
		"lines": v["lines"],
	}
	for k, v in TEMPLATE_PACKS.items()
]


def get_template_pack(template_code: str | None = None, building_type: str | None = None) -> dict | None:
	if template_code and template_code in TEMPLATE_PACKS:
		return TEMPLATE_PACKS[template_code]
	if building_type:
		meta = BUILDING_TYPE_META.get(building_type, {})
		code = meta.get("template_code")
		if code:
			return TEMPLATE_PACKS.get(code)
	return None
