/* Minimal offline shell for construction mobile hub (cache static assets only). */
const CACHE = "omnexa-construction-v1";
const ASSETS = ["/assets/omnexa_construction/js/construction_sw.js"];

self.addEventListener("install", (event) => {
	event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("fetch", (event) => {
	if (event.request.method !== "GET") return;
	event.respondWith(
		caches.match(event.request).then((cached) => cached || fetch(event.request))
	);
});
