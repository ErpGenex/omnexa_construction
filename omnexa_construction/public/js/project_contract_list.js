// Fix stale route_options from 3-tuple Number Cards (key "status.=" → Invalid filter: =)
frappe.listview_settings["Project Contract"] = {
	onload(listview) {
		if (!frappe.route_options) {
			return;
		}
		const cleaned = {};
		let changed = false;
		for (const [key, value] of Object.entries(frappe.route_options)) {
			if (key.includes(".=") || key.endsWith(".!=")) {
				changed = true;
				const field = key.split(".")[0];
				if (Array.isArray(value) && value.length >= 2) {
					cleaned[field] = [value[0], value[1]];
				}
				continue;
			}
			cleaned[key] = value;
		}
		if (changed) {
			frappe.route_options = cleaned;
		}
	},
};
