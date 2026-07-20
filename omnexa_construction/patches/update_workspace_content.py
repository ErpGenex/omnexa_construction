# Patch to update workspace content with new shortcuts

import frappe
import json


def execute():
	"""Update workspace content with new shortcuts"""
	try:
		workspace = frappe.get_doc("Workspace", "Construction")
		
		# Get current content
		content = json.loads(workspace.content or "[]")
		
		# Add new shortcuts to Quick Actions
		new_shortcuts = [
			{
				"id": "construction-qa-primavera",
				"type": "shortcut",
				"data": {"shortcut_name": "Primavera P6 Sync Dashboard", "col": 4
	}
			},
			{
				"id": "construction-qa-portfolio",
				"type": "shortcut",
				"data": {"shortcut_name": "Portfolio Dashboard", "col": 4
	}
			},
			{
				"id": "construction-qa-bim",
				"type": "shortcut",
				"data": {"shortcut_name": "BIM IFC Viewer", "col": 4
	}
			}
		]
		
		# Find Quick Actions header and add shortcuts after it
		quick_actions_index = -1
		for i, item in enumerate(content):
			if item.get("type") == "header" and "Quick Actions" in item.get("data", {}).get("text", ""):
				quick_actions_index = i
				break
		
		if quick_actions_index >= 0:
			# Insert new shortcuts after Quick Actions header
			for shortcut in new_shortcuts:
				content.insert(quick_actions_index + 1, shortcut)
		
		# Update workspace content
		workspace.content = json.dumps(content)
		workspace.save()
		
		frappe.logger("omnexa_construction").info("Workspace content updated successfully")
		
	except Exception as e:
		frappe.logger("omnexa_construction").error("Failed to update workspace content: %s", str(e))
