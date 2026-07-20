frappe.ui.form.on("BOQ Item", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.is_group) {
			return;
		}
		if (frm.doc.material_bom && frm.doc.material_bom.length && frappe.boot.doctypes["Stock Entry"]) {
			frm.add_custom_button(
				__("Material Issue from BOM"),
				() => {
					frappe.call({
						method: "omnexa_construction.inventory_hooks.create_material_issue_from_boq",
						args: { boq_item: frm.doc.name },
						callback(r) {
							if (r.message) {
								frappe.set_route("Form", "Stock Entry", r.message);
							}
						},
					});
				},
				__("Inventory")
			);
		}
	},
});
