frappe.pages["construction-site-mobile"].on_page_load = function (wrapper) {
	if (!document.querySelector('link[rel="manifest"][href*="construction-site-pwa"]')) {
		const link = document.createElement("link");
		link.rel = "manifest";
		link.href = "/assets/omnexa_construction/construction-site-pwa.webmanifest";
		document.head.appendChild(link);
	}

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
		["Construction OSHA Site Checklist", __("OSHA Checklist"), "red"],
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
		html += `<div class="mt-3 card"><div class="card-body"><h6>${__("Field capture")}</h6>`;
		html += `<button class="btn btn-default btn-sm" id="btn-gps">${__("Capture GPS")}</button> `;
		html += `<span id="gps-label" class="text-muted small"></span><br class="mb-2">`;
		html += `<input type="file" accept="image/*" capture="environment" id="site-photo" class="mt-2">`;
		html += `<canvas id="sig-canvas" width="300" height="80" style="border:1px solid #ccc;display:block;margin-top:8px;"></canvas>`;
		html += `<button class="btn btn-default btn-xs mt-1" id="btn-clear-sig">${__("Clear signature")}</button></div></div>`;
		html += `<div class="mt-3"><button class="btn btn-default btn-sm" id="btn-draft-offline">${__("Save Draft Offline")}</button> `;
		html += `<button class="btn btn-primary btn-sm" id="btn-sync-queue">${__("Sync Queue")} (${queue.length})</button></div>`;
		html += `<p class="text-muted small mt-2">${__("Drafts are stored locally and synced when online.")}</p>`;
		html += `<div class="mt-3 card"><div class="card-body"><h6>${__("Site invoice OCR (paste text)")}</h6>`;
		html += `<textarea class="form-control input-sm" id="ocr-raw" rows="4" placeholder="${__("Paste invoice lines…")}"></textarea>`;
		html += `<button class="btn btn-default btn-sm mt-2" id="btn-parse-invoice">${__("Parse & match BOQ")}</button>`;
		html += `<pre class="small mt-2" id="ocr-result"></pre></div></div>`;
		if (queue.length) {
			html += `<ul class="list-unstyled small">${queue
				.map((r) => `<li>${r.doctype}: ${r.subject || r.name || __("draft")}</li>`)
				.join("")}</ul>`;
		}
		$(page.body).html(html);

		$(page.body).on("click", ".mobile-hub-btn", function () {
			frappe.new_doc($(this).data("dt"));
		});
		let gps = null;
		$(page.body).on("click", "#btn-gps", () => {
			if (!navigator.geolocation) {
				frappe.msgprint(__("GPS not available on this device."));
				return;
			}
			navigator.geolocation.getCurrentPosition((pos) => {
				gps = { lat: pos.coords.latitude, lng: pos.coords.longitude };
				$(page.body).find("#gps-label").text(`${gps.lat.toFixed(5)}, ${gps.lng.toFixed(5)}`);
			});
		});
		const canvas = $(page.body).find("#sig-canvas")[0];
		if (canvas) {
			const ctx = canvas.getContext("2d");
			let drawing = false;
			canvas.onmousedown = () => (drawing = true);
			canvas.onmouseup = () => (drawing = false);
			canvas.onmousemove = (e) => {
				if (!drawing) return;
				const r = canvas.getBoundingClientRect();
				ctx.lineWidth = 2;
				ctx.lineTo(e.clientX - r.left, e.clientY - r.top);
				ctx.stroke();
			};
			$(page.body).on("click", "#btn-clear-sig", () => {
				ctx.clearRect(0, 0, canvas.width, canvas.height);
			});
		}
		$(page.body).on("click", "#btn-draft-offline", () => {
			const q = loadQueue();
			const item = { doctype: "Site Daily Report", subject: __("Draft"), ts: Date.now(), draft: {} };
			if (gps) {
				item.draft.gps_latitude = gps.lat;
				item.draft.gps_longitude = gps.lng;
			}
			const photo = $(page.body).find("#site-photo")[0];
			if (photo?.files?.[0]) {
				const reader = new FileReader();
				reader.onload = () => {
					item.photo_base64 = reader.result;
					if (canvas) item.signature_base64 = canvas.toDataURL();
					q.push(item);
					saveQueue(q);
					frappe.show_alert({ message: __("Draft saved offline"), indicator: "green" });
					render();
				};
				reader.readAsDataURL(photo.files[0]);
				return;
			}
			if (canvas) item.signature_base64 = canvas.toDataURL();
			q.push(item);
			saveQueue(q);
			frappe.show_alert({ message: __("Draft saved offline"), indicator: "green" });
			render();
		});
		$(page.body).on("click", "#btn-parse-invoice", () => {
			const raw = $(page.body).find("#ocr-raw").val();
			const contract = frappe.route_options?.project_contract;
			if (!contract) {
				frappe.msgprint(__("Open from a Project Contract or set route_options.project_contract."));
				return;
			}
			frappe.call({
				method: "omnexa_construction.site_invoice_ocr.parse_site_invoice_text",
				args: { raw_text: raw, project_contract: contract },
				callback(r) {
					$(page.body).find("#ocr-result").text(JSON.stringify(r.message || {}, null, 2));
				},
			});
		});
		$(page.body).on("click", "#btn-sync-queue", () => {
			const q = loadQueue();
			if (!q.length) {
				frappe.show_alert({ message: __("Queue empty"), indicator: "blue" });
				return;
			}
			frappe.call({
				method: "omnexa_construction.mobile_field_hub.sync_offline_queue_enhanced",
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
