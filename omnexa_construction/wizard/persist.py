from __future__ import annotations

import frappe


def save_wizard_setup(setup, *, ignore_version: bool = True) -> None:
	"""Persist wizard draft; concurrent step saves must not raise TimestampMismatchError."""
	setup.flags.ignore_permissions = True
	setup.flags.wizard_save = True
	setup.save(ignore_version=ignore_version)
