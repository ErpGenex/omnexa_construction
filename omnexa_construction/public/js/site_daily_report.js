frappe.ui.form.on("Site Daily Report", {
	refresh(frm) {
		if (frm.is_new() && navigator.geolocation) {
			frm.add_custom_button(__("Capture GPS"), () => {
				navigator.geolocation.getCurrentPosition((pos) => {
					frm.set_value("latitude", pos.coords.latitude);
					frm.set_value("longitude", pos.coords.longitude);
					frappe.show_alert({ message: __("Location captured"), indicator: "green" });
				});
			});
		}
	},
});
