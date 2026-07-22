/* global frappe */
(function () {
const STORAGE_LANG = "const_site_lang";

const JOURNEY_STEPS = [
{ ar: "تخطيط", en: "Planning", desc_ar: "تخطيط المشروع", desc_en: "Project planning", icon: "📋" },
{ ar: "تصميم", en: "Design", desc_ar: "تصميم معماري", desc_en: "Architectural design", icon: "📐" },
{ ar: "موافقات", en: "Approvals", desc_ar: "الحصول على التراخيص", desc_en: "Obtaining permits", icon: "📄" },
{ ar: "بناء", en: "Construction", desc_ar: "أعمال البناء", desc_en: "Construction works", icon: "🏗️" },
{ ar: "تشطيب", en: "Finishing", desc_ar: "أعمال التشطيب", desc_en: "Finishing works", icon: "🎨" },
{ ar: "تسليم", en: "Handover", desc_ar: "تسليم المفتاح", desc_en: "Key handover", icon: "🔑" },
];

const NAV_MEGA = [
{
key: "about",
ar: "عن الشركة",
en: "About",
items: [
{ href: "/construction#const-services-section", ar: "خدماتنا", en: "Our Services" },
{ href: "/construction#const-partners-section", ar: "شركاؤنا", en: "Partners" },
{ href: "/construction#const-news-section", ar: "الأخبار", en: "News" },
],
},
{
key: "services",
ar: "خدمات",
en: "Services",
items: [
{ href: "/construction#const-residential-section", ar: "سكني", en: "Residential" },
{ href: "/construction#const-commercial-section", ar: "تجاري", en: "Commercial" },
{ href: "/construction#const-industrial-section", ar: "صناعي", en: "Industrial" },
],
},
{
key: "projects",
ar: "المشاريع",
en: "Projects",
items: [
{ href: "/construction#const-projects-section", ar: "مشاريعنا", en: "Our Projects" },
{ href: "/construction#const-portfolio-section", ar: "معرض الأعمال", en: "Portfolio" },
],
},
{
key: "portals",
ar: "البوابات",
en: "Portals",
items: [
{ href: "__DESK__/construction-workcenter", ar: "مركز العمل", en: "Workcenter" },
{ href: "__DESK__/construction-customer-portal", ar: "بوابة البناء", en: "Construction Portal" },
],
},
];

const DEFAULT_CATALOG = {
services: [
{ key: "residential", name_ar: "بناء سكني", name_en: "Residential Construction", image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80" },
{ key: "commercial", name_ar: "بناء تجاري", name_en: "Commercial Construction", image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80" },
{ key: "industrial", name_ar: "بناء صناعي", name_en: "Industrial Construction", image: "https://images.unsplash.com/photo-1565793298595-6a879b1d9492?auto=format&fit=crop&w=800&q=80" },
{ key: "renovation", name_ar: "ترميم وتجديد", name_en: "Renovation & Restoration", image: "https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80" },
],
gallery: [
"https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80",
"https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
"https://images.unsplash.com/photo-1565793298595-6a879b1d9492?auto=format&fit=crop&w=800&q=80",
"https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=800&q=80",
"https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
"https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
],
news: [
{ tag_ar: "إعلان", tag_en: "Announcement", title_ar: "افتتاح مشروع سكني جديد", title_en: "New Residential Project Launched", date: "2026-06-01", image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=600&q=70" },
{ tag_ar: "خبر", tag_en: "News", title_ar: "تسليم برج تجاري", title_en: "Commercial Tower Delivered", date: "2026-05-15", image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=70" },
],
projects: [
{ project: "Residential", name: "Residential", name_ar: "سكني", image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80" },
{ project: "Commercial", name: "Commercial", name_ar: "تجاري", image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80" },
{ project: "Industrial", name: "Industrial", name_ar: "صناعي", image: "https://images.unsplash.com/photo-1565793298595-6a879b1d9492?auto=format&fit=crop&w=800&q=80" },
],
};

const ROLES = [
{ icon: "👔", ar: "مدير مشروع", en: "Project Manager" },
{ icon: "👷", ar: "مهندس موقع", en: "Site Engineer" },
{ icon: "🏗️", ar: "مشرف بناء", en: "Construction Supervisor" },
{ icon: "📋", ar: "مخطط", en: "Planner" },
{ icon: "✅", ar: "مراقب جودة", en: "Quality Inspector" },
{ icon: "📊", ar: "كمسير", en: "Quantity Surveyor" },
{ icon: "💰", ar: "مالية", en: "Finance" },
];

window.ConstSite = {
config: null,
lang: localStorage.getItem(STORAGE_LANG) || "ar",
page: "home",

init(page) {
this.page = page || "home";
this.config = this.defaultConfig();
this.applyTheme();
this.renderChrome();
this.loadConfig();
const fn = this[`init_${this.page}`];
if (typeof fn === "function") fn.call(this);
this.setupReveal();
},

defaultConfig() {
return {
brand_name_ar: "Omnexa Construction",
brand_name_en: "Omnexa Construction",
tagline_ar: "بناء المستقبل بأيدٍ خبيرة",
tagline_en: "Building the future with expert hands",
hero_text_ar: "بناء سكني، تجاري، وصناعي بجودة عالية",
hero_text_en: "Residential, commercial, and industrial construction with high quality",
hero_image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1920&q=85",
logo: "/assets/omnexa_construction/construction.svg",
primary_color: "#b45309",
secondary_color: "#d97706",
accent_color: "#fde68a",
gold_color: "#f59e0b",
services: DEFAULT_CATALOG.services,
gallery: DEFAULT_CATALOG.gallery,
news: DEFAULT_CATALOG.news,
projects: DEFAULT_CATALOG.projects,
hero_stats: { clients: 200, projects: 500, built: 1000000, countries: 15 },
stats: { sites: 20, workers: 2000, ongoing: 35, completed: 465 },
urls: {
home: "/construction",
desk: "/app/construction-workcenter",
portal: "/app/construction-customer-portal",
},
};
},

t(key) {
const map = {
home: { ar: "الرئيسية", en: "Home" },
services: { ar: "الخدمات", en: "Services" },
projects: { ar: "المشاريع", en: "Projects" },
login: { ar: "دخول", en: "Login" },
desk: { ar: "مركز العمل", en: "Workcenter" },
journey_title: { ar: "رحلة البناء المتكاملة", en: "Complete Construction Journey" },
journey_sub: { ar: "من التخطيط حتى التسليم — إدارة واحدة", en: "From planning to handover" },
roles_title: { ar: "بوابات لكل دور", en: "Portal for Every Role" },
roles_sub: { ar: "أدوار متعددة — لوحة مخصصة لكل مستوى", en: "Multiple roles — tailored dashboards" },
cta_title: { ar: "جاهزون لبناء مشروعك؟", en: "Ready to build your project?" },
cta_sub: {
ar: "انضم إلى Omnexa Construction أو سجّل دخولك إلى المنصة",
en: "Join Omnexa Construction or sign in to the platform",
},
loading: { ar: "جاري التحميل...", en: "Loading..." },
clients: { ar: "عملاء", en: "Clients" },
projects: { ar: "مشاريع", en: "Projects" },
built: { ar: "متر مربع", en: "Sq Meters Built" },
sites: { ar: "مواقع", en: "Sites" },
workers: { ar: "عمال", en: "Workers" },
ongoing: { ar: "قيد البناء", en: "Ongoing" },
completed: { ar: "مكتمل", en: "Completed" },
};
return (map[key] && map[key][this.lang]) || key;
},

esc(v) {
if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
return frappe.utils.escape_html(v == null ? "" : String(v));
}
const d = document.createElement("div");
d.textContent = v == null ? "" : String(v);
return d.innerHTML;
},

deskPortalHref(page) {
const dest = `/app/${String(page || "").replace(/^\/+/, "")}`;
const user = typeof frappe !== "undefined" && frappe.session ? frappe.session.user : "Guest";
if (user && user !== "Guest") return dest;
return `/login?redirect-to=${encodeURIComponent(dest)}`;
},

resolveHref(href) {
if (!href) return "#";
if (href.startsWith("__DESK__/")) {
return this.deskPortalHref(href.slice("__DESK__/".length));
}
return href;
},

nameField() {
return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
},

textField(base) {
return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
},

loadConfig() {
this.config = this.config || this.defaultConfig();
if (this.config.primary_color) {
document.documentElement.style.setProperty("--const-primary", this.config.primary_color);
}
if (this.config.secondary_color) {
document.documentElement.style.setProperty("--const-secondary", this.config.secondary_color);
}
if (this.config.accent_color) {
document.documentElement.style.setProperty("--const-amber-soft", this.config.accent_color);
}
if (this.config.gold_color) {
document.documentElement.style.setProperty("--const-amber", this.config.gold_color);
}
},

applyTheme() {
const root = document.querySelector(".const-site");
if (!root) return;
root.dir = this.lang === "ar" ? "rtl" : "ltr";
root.lang = this.lang;
},

toggleLang() {
this.lang = this.lang === "ar" ? "en" : "ar";
localStorage.setItem(STORAGE_LANG, this.lang);
this.applyTheme();
this.renderChrome();
const fn = this[`init_${this.page}`];
if (typeof fn === "function") fn.call(this);
},

setupReveal() {
const els = document.querySelectorAll(".const-reveal");
if (!els.length || !("IntersectionObserver" in window)) {
els.forEach((el) => el.classList.add("const-visible"));
return;
}
const obs = new IntersectionObserver(
(entries) => {
entries.forEach((e) => {
if (e.isIntersecting) {
e.target.classList.add("const-visible");
obs.unobserve(e.target);
}
});
},
{ threshold: 0.12 }
);
els.forEach((el) => obs.observe(el));
},

renderChrome() {
const cfg = this.config || this.defaultConfig();
const name = cfg[this.nameField()] || "Omnexa Construction";
const logo = cfg.logo
? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
: "🏗️";
const nav = [
{ href: "/construction", key: "home", page: "home" },
{ href: "/construction#const-services-section", ar: "الخدمات", en: "Services", page: "" },
{ href: "/construction#const-projects-section", ar: "المشاريع", en: "Projects", page: "" },
{ href: "/construction#const-portfolio-section", ar: "معرض الأعمال", en: "Portfolio", page: "" },
];
const megaHtml = NAV_MEGA.map(
(m) => `
<div class="const-mega-item">
<button type="button" class="const-mega-trigger">${this.lang === "ar" ? m.ar : m.en} ▾</button>
<div class="const-mega-panel">
${m.items
.map(
(it) =>
`<a href="${this.esc(this.resolveHref(it.href))}" ${it.external ? 'target="_blank" rel="noopener"' : ""}>${this.lang === "ar" ? it.ar : it.en}</a>`
)
.join("")}
</div>
</div>`
).join("");

const header = document.getElementById("const-header");
if (header) {
header.innerHTML = `
<div class="const-topbar"><div class="const-wrap const-topbar-inner">
<span>📞 +966 11 000 0000</span>
<span>✉ info@omnexa.construction</span>
<span class="const-topbar-links">
<a href="${this.esc(this.deskPortalHref("construction-workcenter"))}">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
<a href="${this.esc(this.deskPortalHref("construction-customer-portal"))}">${this.lang === "ar" ? "البوابة" : "Portal"}</a>
</span>
</div></div>
<div class="const-wrap const-header-inner">
<a class="const-brand const-brand-stack" href="/construction">
<span class="const-brand-logo">${logo}</span>
<span class="const-brand-name">${this.esc(name)}</span>
</a>
<button type="button" class="const-mobile-toggle" id="const-menu-toggle" aria-label="Menu">☰</button>
<nav class="const-nav const-nav-single" id="const-nav">
<div class="const-nav-links">
${nav
.map((n) => {
const label = n.key ? this.t(n.key) : this.lang === "ar" ? n.ar : n.en;
const active = n.page && this.page === n.page ? "active" : "";
return `<a href="${n.href}" class="${active}">${label}</a>`;
})
.join("")}
</div>
<div class="const-nav-mega">${megaHtml}</div>
</nav>
<div class="const-actions">
<button type="button" class="const-lang" id="const-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
<a class="const-btn const-btn-outline" href="/login">${this.t("login")}</a>
<a class="const-btn const-btn-primary" href="/construction">${this.t("home")}</a>
</div>
</div>`;
document.getElementById("const-lang-toggle")?.addEventListener("click", () => this.toggleLang());
document.getElementById("const-menu-toggle")?.addEventListener("click", () => {
document.getElementById("const-nav")?.classList.toggle("open");
});
}

const footer = document.getElementById("const-footer");
if (footer) {
const u = cfg.urls || {};
footer.innerHTML = `
<div class="const-wrap const-footer-grid const-footer-premium">
<div>
<h3>${this.esc(name)}</h3>
<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
<p class="const-footer-contact">📞 +966 11 000 0000 · ✉ info@omnexa.construction</p>
</div>
<div>
<h4>${this.lang === "ar" ? "الخدمات" : "Services"}</h4>
<p><a href="/construction#const-residential-section">${this.lang === "ar" ? "بناء سكني" : "Residential Construction"}</a></p>
<p><a href="/construction#const-commercial-section">${this.lang === "ar" ? "بناء تجاري" : "Commercial Construction"}</a></p>
<p><a href="/construction#const-industrial-section">${this.lang === "ar" ? "بناء صناعي" : "Industrial Construction"}</a></p>
</div>
<div>
<h4>${this.lang === "ar" ? "المشاريع" : "Projects"}</h4>
<p><a href="/construction#const-projects-section">${this.lang === "ar" ? "سكني" : "Residential"}</a></p>
<p><a href="/construction#const-projects-section">${this.lang === "ar" ? "تجاري" : "Commercial"}</a></p>
<p><a href="/construction#const-projects-section">${this.lang === "ar" ? "صناعي" : "Industrial"}</a></p>
</div>
<div>
<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
<p><a href="${this.esc(this.deskPortalHref("construction-customer-portal"))}">${this.lang === "ar" ? "بوابة البناء" : "Construction Portal"}</a></p>
<p><a href="${this.esc(this.deskPortalHref("construction-workcenter"))}">${this.t("desk")}</a></p>
</div>
</div>
<div class="const-wrap const-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
}
},

init_home() {
const cfg = this.config || {};
const heroImg = cfg.hero_image || "";
const hs = cfg.hero_stats || {};
const hero = document.getElementById("const-hero");
if (hero) {
hero.innerHTML = `
<div class="const-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
<div class="const-hero-overlay"></div>
<div class="const-wrap const-hero-premium-inner">
<span class="const-eyebrow const-eyebrow-light">Omnexa Construction · Excellence</span>
<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
<p class="const-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
<div class="const-hero-cta">
<a class="const-btn const-btn-accent" href="/construction#const-services-section">${this.lang === "ar" ? "استكشف خدماتنا" : "Explore Our Services"}</a>
<a class="const-btn const-btn-ghost-light" href="/construction#const-projects-section">${this.lang === "ar" ? "المشاريع" : "Projects"}</a>
</div>
<div class="const-hero-stats">
<div><strong>${this._fmtNum(hs.clients || 200)}+</strong><span>${this.t("clients")}</span></div>
<div><strong>${this._fmtNum(hs.projects || 500)}+</strong><span>${this.t("projects")}</span></div>
<div><strong>${this._fmtNum(hs.built || 1000000)}+</strong><span>${this.t("built")}</span></div>
<div><strong>${hs.countries || 15}+</strong><span>${this.lang === "ar" ? "دولة" : "Countries"}</span></div>
</div>
</div>`;
}

const trust = document.getElementById("const-trust-strip");
if (trust) {
const values = [
{ icon: "🏗️", ar: "بناء احترافي", en: "Professional Construction" },
{ icon: "✅", ar: "جودة عالية", en: "High Quality" },
{ icon: "📐", ar: "تصميم مبتكر", en: "Innovative Design" },
{ icon: "🌍", ar: "خدمة عالمية", en: "Global Service" },
{ icon: "🤝", ar: "شراكات قوية", en: "Strong Partnerships" },
];
trust.innerHTML = `<div class="const-wrap const-value-inner">${values
.map((v) => `<div class="const-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
.join("")}</div>`;
}

this.renderServices("const-services-section");

const stats = document.getElementById("const-stats");
if (stats && cfg.stats) {
const s = cfg.stats;
stats.innerHTML = `
<div class="const-wrap const-stats-grid">
<div><div class="const-stat-num">${s.sites || 0}</div><div class="const-stat-label">${this.t("sites")}</div></div>
<div><div class="const-stat-num">${s.workers || 0}</div><div class="const-stat-label">${this.t("workers")}</div></div>
<div><div class="const-stat-num">${s.ongoing || 0}</div><div class="const-stat-label">${this.t("ongoing")}</div></div>
<div><div class="const-stat-num">${s.completed || 0}</div><div class="const-stat-label">${this.t("completed")}</div></div>
</div>`;
}

const journey = document.getElementById("const-process-section");
if (journey) {
const steps = JOURNEY_STEPS;
journey.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Construction Process</span>
<h2>${this.t("journey_title")}</h2>
<p>${this.t("journey_sub")}</p>
</div>
<div class="const-journey const-journey-full">
${steps
.map(
(step, i) => `
<div class="const-journey-step">
<div class="const-journey-num">${step.icon || i + 1}</div>
<h4>${this.lang === "ar" ? step.ar : step.en}</h4>
<p>${this.lang === "ar" ? step.desc_ar : step.desc_en}</p>
</div>`
)
.join("")}
</div>
</div>`;
}

const roles = document.getElementById("const-roles-section");
if (roles) {
roles.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow const-eyebrow-light">Role-Based Access</span>
<h2>${this.t("roles_title")}</h2>
<p>${this.t("roles_sub")}</p>
</div>
<div class="const-roles-grid">
${ROLES.map(
(r) => `
<div class="const-role-card">
<div class="const-role-icon">${r.icon}</div>
<span>${this.lang === "ar" ? r.ar : r.en}</span>
</div>`
).join("")}
</div>
</div>`;
}

const cta = document.getElementById("const-cta-band");
if (cta) {
cta.innerHTML = `
<div class="const-wrap">
<h2>${this.t("cta_title")}</h2>
<p>${this.t("cta_sub")}</p>
<div class="const-cta-actions">
<a class="const-btn const-btn-gold" href="/construction#const-services-section">${this.lang === "ar" ? "ابدأ الآن" : "Get Started"}</a>
<a class="const-btn const-btn-ghost-light" href="${this.deskPortalHref("construction-workcenter")}">${this.t("desk")}</a>
</div>
</div>`;
}

this.renderProjects("const-projects-section");
this.renderResidential("const-residential-section");
this.renderCommercial("const-commercial-section");
this.renderIndustrial("const-industrial-section");
this.renderGallery("const-gallery-section");
this.renderNews("const-news-section");
this.renderPartners("const-partners-section");
},

_fmtNum(n) {
const v = Number(n) || 0;
return v >= 1000 ? Math.round(v / 1000) + "K" : String(v);
},

renderServices(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const services = (this.config && this.config.services) || [];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Our Services</span>
<h2>${this.lang === "ar" ? "خدمات البناء" : "Construction Services"}</h2>
<p>${this.lang === "ar" ? "حلول بناء شاملة لجميع احتياجاتك" : "Comprehensive construction solutions for all your needs"}</p>
</div>
<div class="const-college-grid">
${services
.map(
(s) => `
<div class="const-college-card">
<div class="const-college-img"><img src="${this.esc(s.image)}" alt="" loading="lazy" onerror="this.src='/assets/omnexa_construction/construction.svg'" /></div>
<div class="const-college-body">
<h3>${this.esc(this.lang === "ar" ? s.name_ar : s.name_en)}</h3>
<a class="const-btn const-btn-sm const-btn-primary" href="/construction#const-services-section">${this.lang === "ar" ? "المزيد" : "Learn More"}</a>
</div>
</div>`
)
.join("")}
</div>
</div>`;
},

renderProjects(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const projects = (this.config && this.config.projects) || [];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Project Types</span>
<h2>${this.lang === "ar" ? "أنواع المشاريع" : "Project Types"}</h2>
</div>
<div class="const-type-grid">
${projects
.map(
(row) => `
<div class="const-type-card">
<div class="const-type-img"><img src="${this.esc(row.image)}" alt="" loading="lazy" onerror="this.src='/assets/omnexa_construction/construction.svg'" /></div>
<div class="const-type-body">
<h3>${this.esc(this.lang === "ar" ? row.name_ar : row.name_en)}</h3>
<p class="const-muted">${this.esc(row.project)}</p>
</div>
</div>`
)
.join("")}
</div>
</div>`;
},

renderResidential(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const items =
this.lang === "ar"
? ["فيلات", "شقق", "مجمعات سكنية", "عمارات سكنية", "تجديد سكني"]
: ["Villas", "Apartments", "Residential Complexes", "Residential Towers", "Residential Renovation"];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Residential Construction</span>
<h2>${this.lang === "ar" ? "البناء السكني" : "Residential Construction"}</h2>
</div>
<div class="const-services-grid">
${items.map((t) => `<div class="const-service-card"><span>✓</span>${t}</div>`).join("")}
</div>
</div>`;
},

renderCommercial(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const items =
this.lang === "ar"
? ["أبراج مكاتب", "مراكز تجارية", "فنادق", "مطاعم", "تجديد تجاري"]
: ["Office Towers", "Shopping Centers", "Hotels", "Restaurants", "Commercial Renovation"];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Commercial Construction</span>
<h2>${this.lang === "ar" ? "البناء التجاري" : "Commercial Construction"}</h2>
</div>
<div class="const-services-grid">
${items.map((t) => `<div class="const-service-card"><span>✓</span>${t}</div>`).join("")}
</div>
</div>`;
},

renderIndustrial(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const items =
this.lang === "ar"
? ["مصانع", "مستودعات", "ورش عمل", "منشآت صناعية", "تجديد صناعي"]
: ["Factories", "Warehouses", "Workshops", "Industrial Facilities", "Industrial Renovation"];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Industrial Construction</span>
<h2>${this.lang === "ar" ? "البناء الصناعي" : "Industrial Construction"}</h2>
</div>
<div class="const-services-grid">
${items.map((t) => `<div class="const-service-card"><span>✓</span>${t}</div>`).join("")}
</div>
</div>`;
},

renderGallery(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const fallback = "/assets/omnexa_construction/construction.svg";
const imgs = ((this.config && this.config.gallery) || []).slice();
while (imgs.length < 6) {
imgs.push(imgs[imgs.length % Math.max(imgs.length, 1)] || fallback);
}
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Our Projects</span>
<h2>${this.lang === "ar" ? "مشاريعنا" : "Our Projects"}</h2>
<p>${this.lang === "ar" ? "مشاريع متنوعة في مختلف القطاعات" : "Diverse projects across various sectors"}</p>
</div>
<div class="const-gallery-grid">
${imgs
.slice(0, 6)
.map(
(src, i) =>
`<div class="const-gallery-item ${i === 0 ? "const-gallery-featured" : ""}"><img src="${this.esc(src)}" alt="" loading="lazy" onerror="this.onerror=null;this.src='${fallback}'" /></div>`
)
.join("")}
</div>
</div>`;
},

renderNews(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const rows = (this.config && this.config.news) || [];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">News & Events</span>
<h2>${this.lang === "ar" ? "آخر الأخبار" : "Latest News"}</h2>
</div>
<div class="const-news-grid">
${rows
.map(
(n) => `
<article class="const-news-card">
<div class="const-news-img"><img src="${this.esc(n.image)}" alt="" loading="lazy" /></div>
<div class="const-news-body">
<span class="const-badge">${this.esc(this.lang === "ar" ? n.tag_ar : n.tag_en)}</span>
<h3>${this.esc(this.lang === "ar" ? n.title_ar : n.title_en)}</h3>
<time>${this.esc(n.date)}</time>
</div>
</article>`
)
.join("")}
</div>
</div>`;
},

renderPartners(hostId) {
const host = document.getElementById(hostId);
if (!host) return;
const partners =
this.lang === "ar"
? ["مطورون عقاريون", "شركات استثمار", "حكومات", "مؤسسات خاصة", "أفراد"]
: ["Real Estate Developers", "Investment Companies", "Governments", "Private Institutions", "Individuals"];
host.innerHTML = `
<div class="const-wrap">
<div class="const-section-title">
<span class="const-eyebrow">Partners</span>
<h2>${this.lang === "ar" ? "شركاؤنا" : "Our Partners"}</h2>
</div>
<div class="const-partners-row">${partners.map((p) => `<span class="const-partner-pill">${p}</span>`).join("")}</div>
</div>`;
},
};
})();
