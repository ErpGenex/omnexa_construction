from __future__ import annotations

from frappe.utils import cint, flt

ROAD_TYPES = frozenset({"urban_road", "highway", "tunnel", "railway"})
PIPELINE_TYPES = frozenset(
	{
		"water_network",
		"sewer_network",
		"electrical_network",
		"gas_network",
		"telecom_fiber",
		"district_cooling",
	}
)

SPEC_DEFAULTS_BUILDING = {
	"plot_area_m2": 600.0,
	"gross_floor_area_m2": 450.0,
	"number_of_floors": 2,
	"basement_levels": 0,
	"unit_count": 1,
}

SPEC_DEFAULTS_ROAD = {
	"road_length_m": 800.0,
	"road_width_m": 12.0,
}

SPEC_DEFAULTS_PIPELINE = {
	"pipe_network_km": 5.0,
}

TYPE_OVERRIDES: dict[str, dict] = {
	"hotel": {"key_count": 120, "unit_count": 1},
	"hospital": {"bed_count": 200, "unit_count": 1},
	"social_housing": {"plot_area_m2": 4000.0, "gross_floor_area_m2": 3200.0, "unit_count": 80},
	"office_tower": {"plot_area_m2": 1200.0, "gross_floor_area_m2": 24000.0, "number_of_floors": 25},
	"warehouse": {"plot_area_m2": 5000.0, "gross_floor_area_m2": 4000.0, "number_of_floors": 1},
	"factory": {"plot_area_m2": 8000.0, "gross_floor_area_m2": 6000.0, "number_of_floors": 1},
	"mixed_use": {"plot_area_m2": 1800.0, "gross_floor_area_m2": 42000.0, "number_of_floors": 28, "unit_count": 120},
	"data_center": {"plot_area_m2": 12000.0, "gross_floor_area_m2": 8000.0, "number_of_floors": 2},
	"airport_terminal": {"plot_area_m2": 85000.0, "gross_floor_area_m2": 120000.0, "number_of_floors": 3},
	"stadium": {"plot_area_m2": 45000.0, "gross_floor_area_m2": 28000.0, "unit_count": 40000},
	"metro_station": {"plot_area_m2": 3200.0, "gross_floor_area_m2": 4800.0, "basement_levels": 2},
	"residential_compound": {"plot_area_m2": 85000.0, "gross_floor_area_m2": 12000.0, "unit_count": 48},
	"parking_structure": {"plot_area_m2": 2400.0, "gross_floor_area_m2": 7200.0, "number_of_floors": 6},
	"laboratory": {"plot_area_m2": 4200.0, "gross_floor_area_m2": 6800.0, "number_of_floors": 3},
	"tunnel": {"road_length_m": 2400.0, "road_width_m": 12.0},
	"solar_farm": {"plot_area_m2": 450000.0, "gross_floor_area_m2": 1200.0},
	"power_plant": {"plot_area_m2": 120000.0, "gross_floor_area_m2": 18000.0},
	"railway": {"road_length_m": 12000.0, "road_width_m": 8.0},
	"district_cooling": {"pipe_network_km": 8.0},
}


def spec_category(building_type: str | None) -> str:
	bt = (building_type or "").strip()
	if bt in ROAD_TYPES:
		return "road"
	if bt in PIPELINE_TYPES:
		return "pipeline"
	return "building"


def base_spec_defaults(building_type: str | None) -> dict:
	bt = (building_type or "").strip()
	cat = spec_category(bt)
	if cat == "road":
		defaults = dict(SPEC_DEFAULTS_ROAD)
	elif cat == "pipeline":
		defaults = dict(SPEC_DEFAULTS_PIPELINE)
	else:
		defaults = dict(SPEC_DEFAULTS_BUILDING)
	defaults.update(TYPE_OVERRIDES.get(bt, {}))
	return defaults


def _is_empty_numeric(value, *, allow_zero: bool = False) -> bool:
	if value is None or value == "":
		return True
	num = flt(value)
	if allow_zero and num == 0:
		return False
	return num <= 0


def apply_wizard_spec_defaults(setup, *, force: bool = False) -> dict:
	"""Fill missing specification drivers on Construction Project Setup."""
	bt = (setup.building_type or "").strip()
	if not bt:
		return {}

	changed: dict = {}
	defaults = base_spec_defaults(bt)

	for key, default in defaults.items():
		allow_zero = key == "basement_levels"
		if force or _is_empty_numeric(setup.get(key), allow_zero=allow_zero):
			setup.set(key, default)
			changed[key] = default

	if not setup.quality_tier:
		setup.quality_tier = "Standard"
		changed["quality_tier"] = "Standard"

	return changed
