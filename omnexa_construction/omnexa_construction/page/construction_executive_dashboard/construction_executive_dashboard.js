frappe.pages["construction-executive-dashboard"].on_page_load = function (wrapper) {
	if (window.omnexa_core && omnexa_core.vertical_portal && omnexa_core.vertical_portal.mountRoleDesk) {
		omnexa_core.vertical_portal.mountRoleDesk(wrapper, "omnexa_construction", "executive-dashboard");
		return;
	}
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("construction-executive-dashboard"),
		single_column: true,
	});
	$(page.body).html("<p class=\"text-muted\">" + __("Load omnexa_core vertical portal desk") + "</p>");
};
