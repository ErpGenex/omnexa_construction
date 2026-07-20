# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Autodesk BIM 360 OAuth2 (enterprise) — authorization + token storage."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def get_bim360_authorize_url() -> dict:
	settings = frappe.get_single("Construction Integration Settings")
	client_id = settings.get("bim360_client_id")
	if not client_id:
		frappe.throw(_("Set BIM 360 Client ID in Integration Settings."), title=_("BIM 360"))
	redirect = frappe.utils.get_url("/api/method/omnexa_construction.integrations.bim360_oauth.bim360_oauth_callback")
	state = frappe.generate_hash(length=16)
	frappe.cache.set_value(f"bim360_oauth_state:{state}", frappe.session.user, expires_in_sec=600)
	url = (
		"https://developer.api.autodesk.com/authentication/v2/authorize"
		f"?response_type=code&client_id={client_id}&redirect_uri={redirect}&scope=data:read data:write"
		f"&state={state}"
	)
	return {"authorize_url": url
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def bim360_oauth_callback(code: str | None = None, state: str | None = None):
	if not code or not state:
		frappe.respond_as_web_page(_("BIM 360"), _("Authorization failed."), indicator_color="red")
		return
	cache_key = f"bim360_oauth_state:{state}"
	user = frappe.cache.get_value(cache_key)
	if not user:
		frappe.respond_as_web_page(_("BIM 360"), _("Invalid or expired state."), indicator_color="red")
		return
	frappe.cache().delete_value(cache_key)
	frappe.set_user(user)
	settings = frappe.get_single("Construction Integration Settings")
	settings.bim360_access_token = code  # MVP: store code; exchange in production
	settings.bim360_token_updated = now_datetime()
	settings.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.respond_as_web_page(_("BIM 360"), _("Connected. Return to Desk."), indicator_color="green")


@frappe.whitelist()
def pull_bim360_models(project_contract: str) -> dict:
	from omnexa_construction.integrations.bim360_api import sync_bim_model_to_bim360

	settings = frappe.get_single("Construction Integration Settings")
	if not settings.get("bim360_access_token"):
		frappe.throw(_("Authorize BIM 360 first."), title=_("BIM 360"))
	models = frappe.get_all(
		"Construction BIM Model Register",
		filters={"project_contract": project_contract
	},
		pluck="name",
	)
	synced = [sync_bim_model_to_bim360(m)["payload"] for m in models[:20]]
	return {"synced": len(synced), "models": synced
	}
