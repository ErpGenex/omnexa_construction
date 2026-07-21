# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Public construction website APIs."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import get_url


def get_website_user_home_page(user: str | None = None) -> str:
	"""Return the desk workcenter page for construction users."""
	return "/app/construction-workcenter"


def get_site_config(context: dict | None = None) -> dict:
	"""Return public construction site configuration."""
	return {
		"app_name": "omnexa_construction",
		"title": "Omnexa Construction",
		"title_ar": "أومنيكسا للمقاولات",
		"hero_image": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1920&q=85",
		"base_path": "/construction",
		"workcenter_route": "/app/construction-workcenter",
		"nav_items": [
			{"key": "home", "ar": "الرئيسية", "en": "Home", "href": "/construction"},
			{"key": "services", "ar": "الخدمات", "en": "Services", "href": "/construction/services"},
			{"key": "contact", "ar": "اتصل بنا", "en": "Contact", "href": "/construction/contact", "cta": True},
		],
		"stats": {
			"projects_completed": 400,
			"clients_served": 180,
			"years_experience": 25,
		},
	}


@frappe.whitelist()
def get_public_construction_data() -> dict:
	"""Return public construction data for the website."""
	return {
		"services": [
			{
				"key": "general_contracting",
				"name_ar": "المقاولات العامة",
				"name_en": "General Contracting",
				"desc_ar": "خدمات مقاولات عامة شاملة للمشاريع المختلفة",
				"desc_en": "Comprehensive general contracting services for various projects",
				"icon": "hard-hat",
			},
			{
				"key": "project_management",
				"name_ar": "إدارة المشاريع",
				"name_en": "Project Management",
				"desc_ar": "إدارة مشاريع احترافية من البداية إلى التسليم",
				"desc_en": "Professional project management from start to delivery",
				"icon": "clipboard",
			},
			{
				"key": "construction_supervision",
				"name_ar": "الإشراف على البناء",
				"name_en": "Construction Supervision",
				"desc_ar": "إشراف فني على جميع مراحل البناء والتشييد",
				"desc_en": "Technical supervision of all construction and building phases",
				"icon": "eye",
			},
		],
		"projects": [
			{"name_ar": "المشاريع السكنية", "name_en": "Residential Projects"},
			{"name_ar": "المشاريع التجارية", "name_en": "Commercial Projects"},
			{"name_ar": "المشاريع الصناعية", "name_en": "Industrial Projects"},
			{"name_ar": "البنية التحتية", "name_en": "Infrastructure"},
			{"name_ar": "المشاريع الخاصة", "name_en": "Special Projects"},
		],
		"capabilities": [
			{"name_ar": "إدارة الجودة", "name_en": "Quality Management"},
			{"name_ar": "السلامة والصحة المهنية", "name_en": "Health & Safety"},
			{"name_ar": "التحكم في التكاليف", "name_en": "Cost Control"},
			{"name_ar": "إدارة الوقت", "name_en": "Time Management"},
			{"name_ar": "إدارة المخاطر", "name_en": "Risk Management"},
		],
	}
