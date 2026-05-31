frappe.pages["construction-project-wizard"].on_page_load = function (wrapper) {
	frappe.require(
		[
			"/assets/omnexa_construction/js/wizard_i18n.js",
			"/assets/omnexa_construction/js/construction_project_wizard.js",
		],
		() => {
		const page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Construction Project Wizard"),
			single_column: true,
		});
		new omnexa_construction.ProjectWizard(page);
		}
	);
};
