frappe.pages["construction-workcenter"].on_page_load = function (wrapper) {
	if (window.omnexa_core && omnexa_core.vertical_workcenter && omnexa_core.vertical_workcenter.mount) {
		omnexa_core.vertical_workcenter.mount(wrapper, "omnexa_construction");
		return;
	}
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Construction Workcenter"),
		single_column: true,
	});
	$(page.body).html('<p class="text-muted">' + __("Load omnexa_core vertical workcenter kit") + "</p>");
};
