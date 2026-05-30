// Copyright (c) 2026, Omnexa and contributors
// License: MIT. See license.txt

function setup_company_construction_demo_buttons(frm) {
	const grp = __("Construction demo");
	const demo_btn = (label, fn) => erpgenex.company_demo.demo_btn(frm, label, fn, grp);

	demo_btn(
		__("Seed 5 projects (owners, IPC, subcontractors, costs)"),
		() => {
			frappe.confirm(
				__(
					"Creates five demo project contracts with clients, subcontractors, BOQ, IPC certificates, payment certificates, site diaries, WIP, and purchase orders (when accounting is available). Continue?",
				),
				() => {
					const branch = (frm.doc.production_demo_branch || "").trim() || null;
					frappe.call({
						method: "omnexa_construction.api.seed_construction_demo_from_company",
						args: {
							company: frm.doc.name,
							branch,
							force: 0,
						},
						freeze: true,
						freeze_message: __("Seeding construction demo portfolio..."),
						callback(r) {
							const m = r.message || {};
							if (m.skipped) {
								frappe.msgprint({
									title: __("Already seeded"),
									indicator: "blue",
									message: m.message || __("Construction demo data already exists for this company."),
								});
								return;
							}
							const lines = [
								`${__("Contracts")}: ${(m.contracts || []).length}`,
								`${__("IPC certificates")}: ${m.ipc_certificates || 0}`,
								`${__("BOQ lines")}: ${m.boq_items || 0}`,
								`${__("Subcontract certificates (JE)")}: ${m.gl_posted_spc || 0}`,
								`${__("Purchase orders")}: ${m.purchase_orders || 0}`,
							];
							frappe.msgprint({
								title: __("Construction demo ready"),
								indicator: "green",
								message: (m.message || __("Done.")) + "<br><br>" + lines.join("<br>"),
							});
						},
					});
				},
			);
		},
	);
}

frappe.ui.form.on("Company", {
	refresh(frm) {
		if (window.erpgenex?.company_demo?.register) {
			erpgenex.company_demo.register(setup_company_construction_demo_buttons);
		}
	},
});
