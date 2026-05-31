frappe.provide("omnexa_construction.i18n");

omnexa_construction.i18n.LABELS = {
	en: {
		"Identity": "Identity",
		"Asset Type": "Asset Type",
		"Specifications": "Specifications",
		"Financials": "Financials",
		"BOQ": "BOQ",
		"Phases & IPC": "Phases & IPC",
		"Detail Pricing": "Detail Pricing",
		"Assignments": "Assignments",
		"Generate": "Generate",
		"Language": "Language",
		"Arabic": "Arabic",
		"English": "English",
		"Regional Cost Factor": "Regional Cost Factor",
		"Site Region Code": "Site Region Code",
	},
	ar: {
		"Identity": "هوية المشروع",
		"Asset Type": "نوع الأصل",
		"Specifications": "المواصفات الهندسية",
		"Financials": "المالية والعقد",
		"BOQ": "جدول الكميات",
		"Phases & IPC": "المراحل والمستخلصات",
		"Detail Pricing": "تسعير التفاصيل",
		"Assignments": "الإسناد",
		"Generate": "التوليد",
		"Language": "اللغة",
		"Arabic": "عربي",
		"English": "English",
		"Regional Cost Factor": "معامل التكلفة الإقليمي",
		"Site Region Code": "رمز المنطقة",
	},
};

omnexa_construction.i18n.get_lang = function () {
	return localStorage.getItem("omnexa_wizard_lang") || "en";
};

omnexa_construction.i18n.set_lang = function (lang) {
	localStorage.setItem("omnexa_wizard_lang", lang === "ar" ? "ar" : "en");
};

omnexa_construction.i18n.t = function (key) {
	const lang = omnexa_construction.i18n.get_lang();
	const pack = omnexa_construction.i18n.LABELS[lang] || omnexa_construction.i18n.LABELS.en;
	return pack[key] || __(key);
};
