# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Sync global BOQ catalog (34 project types) and wizard Select options."""


def execute():
	from omnexa_construction.wizard.building_type_registry import sync_building_type_select_options
	from omnexa_construction.wizard.wizard_api import import_seed_templates

	sync_building_type_select_options()
	import_seed_templates(sync_all=True)
