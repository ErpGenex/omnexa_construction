frappe.pages["construction-site-mobile"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Site Mobile Hub"),
		single_column: true,
	});

	const QUEUE_KEY = "omnexa_construction_offline_queue";

	const shortcuts = [
		["Site Daily Report", __("Daily Report"), "orange"],
		["Construction Permit to Work", __("Permit to Work"), "red"],
		["Construction HSE Incident", __("HSE Incident"), "purple"],
		["Construction RFI", __("RFI"), "blue"],
		["Construction NCR", __("NCR"), "yellow"],
	];

	function loadQueue() {
		try {
			return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
		} catch (e) {
			return [];
		}
	}

	function saveQueue(q) {
		localStorage.setItem(QUEUE_KEY, JSON.stringify(q));
	}

	function render() {
		const queue = loadQueue();
		let html = '<div class="row construction-mobile-hub">';
		shortcuts.forEach(([doctype, label, color]) => {
			if (!frappe.boot.doctypes[doctype]) return;
			html +=
				`<div class="col-sm-6 col-md-4 mb-3">` +
				`<button class="btn btn-${color} btn-block btn-lg mobile-hub-btn" data-dt="${doctype}">${label}</button>` +
				`</div>`;
		});
		html += "</div>";
		html += `<div class="mt-3"><button class="btn btn-default btn-sm" id="btn-draft-offline">${__("Save Draft Offline")}</button> `;
		html += `<button class="btn btn-primary btn-sm" id="btn-sync-queue">${__("Sync Queue")} (${queue.length})</button></div>`;
		html += `<p class="text-muted small mt-2">${__("Drafts are stored locally and synced when online.")}</p>`;
		if (queue.length) {
			html += `<ul class="list-unstyled small">${queue
				.map((r) => `<li>${r.doctype}: ${r.subject || r.name || __("draft")}</li>`)
				.join("")}</ul>`;
		}
		$(page.body).html(html);

		$(page.body).on("click", ".mobile-hub-btn", function () {
			frappe.new_doc($(this).data("dt"));
		});
		$(page.body).on("click", "#btn-draft-offline", () => {
			const q = loadQueue();
			q.push({ doctype: "Site Daily Report", subject: __("Draft"), ts: Date.now(), draft: {} });
			saveQueue(q);
			frappe.show_alert({ message: __("Draft saved offline"), indicator: "green" });
			render();
		});
		$(page.body).on("click", "#btn-sync-queue", () => {
			const q = loadQueue();
			if (!q.length) {
				frappe.show_alert({ message: __("Queue empty"), indicator: "blue" });
				return;
			}
			frappe.call({
				method: "omnexa_construction.mobile_offline.sync_offline_queue",
				args: { queue_json: JSON.stringify(q) },
				callback(r) {
					if (r.message && r.message.synced) {
						saveQueue(q.slice(r.message.synced));
						frappe.show_alert({
							message: __("Synced {0} item(s)", [r.message.synced]),
							indicator: "green",
						});
						render();
					}
				},
			});
		});
	}

	render();

	if ("serviceWorker" in navigator) {
		navigator.serviceWorker.register("/assets/omnexa_construction/js/construction_sw.js").catch(() => {});
	}
};
