# خطة استكمال نواقص Omnexa Construction

**التطبيق:** `omnexa_construction` (ErpGenEx — Construction)  
**الإصدار المستهدف:** v2.0 (امتثال دولي + تشغيل ميداني)  
**تاريخ الخطة:** يونيو 2026  
**مرجع التقييم:** تقرير المعايير الدولية (FIDIC / PMBOK / ISO / NEC4 / ERP)

---

## 1. الهدف والنطاق

### 1.1 الهدف
إغلاق **جميع النواقص** المحددة في تقييم المعايير العالمية، وتحويل التطبيق من **عمود إنشائي متقدم (mid-market)** إلى منصة **جاهزة للمشاريع الدولية والحوكمة الكاملة**.

### 1.2 نطاق الخطة
| داخل النطاق | خارج النطاق (تطبيقات شقيقة) |
|-------------|------------------------------|
| DocTypes، Workflows، تقارير، طباعة، hooks | محاسبة GL كاملة → `omnexa_accounting` |
| EVM، LD، FIDIC، QHSE، CDE، RFQ/PO | جدولة CPM متقدمة → `omnexa_projects_pm` |
| أدوار، اختبارات، i18n | Workflow استشاري صارم → `omnexa_engineering_consulting` |
| تكامل مخزون ERPNext | تطبيق جوال native (مرحلة لاحقة اختيارية) |

### 1.3 مؤشرات النجاح (KPIs)
| المؤشر | خط الأساس | الهدف |
|--------|-----------|--------|
| DocTypes | 53 | ~75 (+22) |
| مستندات Submittable تجارية | 3 | ≥12 |
| Workflows مدمجة | 0 | ≥10 |
| تغطية اختبارات (ملفات) | 25 | ≥45 |
| ترجمة ar.csv | 3 سطور | ≥500 مفتاح |
| امتثال FIDIC (قائمة تحقق) | ~55% | ≥90% |
| امتثال ISO 9001/45001/14001 (عمليات) | ~25% | ≥70% |

---

## 2. الوضع الحالي (ملخص)

### 2.1 موجود ويُبنى عليه
- **عقد:** `Project Contract` (FIDIC/NEC، LD، DLP، احتجاز)
- **تجاري:** `IPC Certificate`, `Construction Change Order`, `Construction Extension of Time`, `Construction Claim`, `Construction FIDIC Notice`, `Construction Final Account Statement`, `Construction DLP Record`
- **كميات:** `BOQ Item`, `Construction QS Measurement Sheet`
- **موقع:** نماذج اعتماد خامات/أعمال، تأخير، غرامات، كشف حساب + طباعة عربية
- **باطن:** `Subcontract Work Order`, `Subcontract Payment Certificate`
- **جودة جزئية:** `Construction NCR`, `Construction Inspection Request`, `Construction Inspection Test Plan`
- **HSE جزئي:** `Construction HSE Incident`
- **مستندات:** `Construction CDE Document`, `Construction Document Transmittal`
- **تقارير:** 8 script reports + EVM + cost rollup
- **معالج:** Construction Project Wizard (8 خطوات)

### 2.2 الفجوات الرئيسية (ملخص)
1. Workflows واعتمادات رسمية على المستندات التجارية  
2. LD آلي وربط تأخير/غرامات → IPC  
3. نزاعات FIDIC / NEC  
4. EVM من جدولة WBS حقيقية  
5. ISO QMS / OH&S / Environment كأنظمة  
6. BIM / ISO 19650 كامل  
7. RFI، ضرائب، مخزون، عملات  
8. اختبارات وi18n وأدوار متخصصة  

---

## 3. هيكل التنفيذ — 6 مراحل

```
المرحلة 0 ──► الأساس (حوكمة + توثيق)           [أسبوع 1–2]
المرحلة 1 ──► التجاري FIDIC (Workflow + LD)    [أسبوع 3–8]
المرحلة 2 ──► الجدولة + EVM + التكلفة          [أسبوع 9–12]
المرحلة 3 ──► QHSE + ISO                        [أسبوع 13–18]
المرحلة 4 ──► مستندات + BIM + تعاون الموقع     [أسبوع 19–24]
المرحلة 5 ──► ERP (مخزون، ضرائب، عملات)        [أسبوع 25–30]
المرحلة 6 ──► NEC4 + نزاعات + BI + جوال        [أسبوع 31–40]
```

**المدة الإجمالية المقدرة:** 9–10 أشهر (فريق 2–3 مطورين + QA جزء من الوقت)

---

## المرحلة 0 — الأساس والحوكمة
**المدة:** أسبوعان | **الأولوية:** P0

### 0.1 توثيق ومحاذاة
| المهمة | المخرج | المسار |
|--------|--------|--------|
| تحديث SAP Parity Checklist | أرقام صحيحة (53 DT، 25+ tests) | `docs/SAP_PARITY_CHECKLIST.md` |
| قائمة تحقق FIDIC | `docs/FIDIC_COMPLIANCE_CHECKLIST.md` | جديد |
| قائمة تحقق ISO | `docs/ISO_COMPLIANCE_CHECKLIST.md` | جديد |
| ربط هذه الخطة بالـ README | قسم Roadmap | `README.md` |

### 0.2 أدوار وصلاحيات
| الدور الجديد | الصلاحيات |
|--------------|-----------|
| Construction QS | BOQ, QS Sheet, Measurement, Reports |
| Construction Commercial Manager | IPC, Change Order, Claim, Final Account |
| Construction HSE Officer | HSE, PTW, Risk Register |
| Construction QA Manager | NCR, ITP, Inspection, CAPA |
| Construction Document Controller | CDE, Transmittal, RFI |

**التنفيذ:**
- Patch: `patches/v1_0/ensure_construction_specialist_roles.py`
- تحديث `permissions` في كل DocType JSON
- ربط `permission_query_conditions` في `hooks.py` إن لزم

### 0.3 جعل المستندات التجارية قابلة للإرسال
| DocType | إجراء |
|---------|--------|
| `IPC Certificate` | `is_submittable: 1` + docstatus |
| `Construction Change Order` | submittable |
| `Construction Extension of Time` | submittable |
| `Construction Claim` | submittable |
| `Construction FIDIC Notice` | submittable (أو Workflow خفيف) |
| `Construction Final Account Statement` | submittable |
| `Construction Fines Statement` | submittable |
| `Construction Work Delay Notice` | submittable |

**ملفات:** `omnexa_construction/doctype/*/…json` + server scripts للتحقق عند Submit

### 0.4 اختبارات أساسية للمرحلة
- `tests/test_commercial_submittable.py`
- `tests/test_construction_roles.py`

**معيار القبول:** Submit/Cancel يعمل؛ الأدوار الجديدة ترى فقط مستندات فرعها.

---

## المرحلة 1 — التجاري FIDIC/NEC (الأولوية القصوى)
**المدة:** 6 أسابيع | **الأولوية:** P0

### 1.1 Workflows (Frappe Workflow)
| Workflow | DocType | الحالات المقترحة |
|----------|---------|------------------|
| IPC Approval | `IPC Certificate` | Draft → QS Review → Commercial → PM → Certified → Posted |
| Change Order | `Construction Change Order` | Draft → Priced → Client Approved → Implemented |
| EOT | `Construction Extension of Time` | Draft → Submitted → Assessed → Approved/Rejected |
| Claim | `Construction Claim` | Draft → Notified → Substantiated → Settled/Rejected |
| Final Account | `Construction Final Account Statement` | Draft → Reconciled → Agreed → Closed |
| Subcontract Cert | `Subcontract Payment Certificate` | Draft → Site → Commercial → Approved → Paid |

**التنفيذ:**
- `omnexa_construction/workflow/` (JSON exports أو patch يُنشئ Workflow)
- Patch: `ensure_construction_commercial_workflows.py`
- `workflow_hooks.py`: توسيع التحقق عند تفعيل `omnexa_engineering_consulting`
- Client scripts: `public/js/ipc_certificate.js` (أزرار حسب الحالة)

### 1.2 محرك غرامات التأخير (LD Engine)
**وحدة جديدة:** `omnexa_construction/liquidated_damages.py`

| الوظيفة | الوصف |
|---------|--------|
| `calc_delay_days()` | من `Construction Work Delay Notice` أو مقارنة تواريخ BOQ/WBS |
| `calc_ld_amount()` | أيام × `liquidated_damages_per_day` مع سقف `liquidated_damages_cap_percent` |
| `apply_ld_to_ipc()` | يملأ `penalty_deduction` على `IPC Certificate` |
| `link_fines_statement()` | تجميع `Construction Fines Statement` → خصم IPC |

**ربط:**
- Hook على Submit: `Construction Work Delay Notice` → اقتراح LD
- زر على `IPC Certificate`: "Calculate Deductions"
- Patch حقول إن لزم: `ld_reference`, `ld_calculation_notes`

### 1.3 ربط FIDIC Notice ↔ Claim ↔ EOT
| المهمة | التفاصيل |
|--------|----------|
| حقول ربط | `linked_claim`, `linked_eot`, `linked_change_order` على Notice |
| Time-bar | `notice_due_date`, `is_time_barred` (حساب 28/42 يوم حسب `governing_standard`) |
| Scheduler | توسيع `fidic_alerts.py` → إشعار + تعليم Time-barred |
| Dashboard | تقرير `Construction FIDIC Compliance` |

**DocType تعديلات:** `construction_fidic_notice.json`, `construction_claim.json`

### 1.4 تحسين IPC (شهادة دفع FIDIC)
| الميزة | التنفيذ |
|--------|---------|
| كميات من QS | زر "Pull from QS Sheet" → `IPC BOQ Line` |
| شهادة مهندس | حقول `engineer_certified_by`, `engineer_cert_date`, مرفق PDF |
| VAT / WHT | حقول `vat_percent`, `vat_amount`, `wht_percent`, `wht_amount`, `net_after_tax` |
| طباعة محدثة | `ipc_certificate_ar.html` + نسخة EN |

### 1.5 أوامر التغيير المتقدمة
| الميزة | DocType/ملف |
|--------|-------------|
| نوع التغيير | Select: Instruction / Proposal / Daywork |
| BOQ مؤقت | Child: `Construction Change Order BOQ Line` |
| تحديث BOQ تلقائي | عند Implemented → `boq_item` quantities/rates |

### 1.6 الحساب الختامي + DLP
| DocType جديد | الغرض |
|--------------|--------|
| `Construction Snagging Item` | قائمة عيوب (punch list) |
| `Construction Retention Release` | إفراج احتجاز مرحلي/نهائي |

**توسيع:** `Construction DLP Record` ← ربط Snagging + `open_defects_count` محسوب

### 1.7 طباعة وتقارير المرحلة 1
- تقرير: `Construction Commercial Pipeline`
- تحديث: `Construction Contract Control`, `IPC Certificate Summary`

### 1.8 اختبارات المرحلة 1
- `test_liquidated_damages.py`
- `test_fidic_time_bar.py`
- `test_ipc_workflow.py`
- `test_change_order_boq_update.py`

**معيار القبول:** IPC يمر Workflow كاملاً؛ LD يُحسب ويظهر على المستخلص؛ إشعار متأخر يُعلَّم time-barred.

---

## المرحلة 2 — الجدولة والتكلفة (PMBOK)
**المدة:** 4 أسابيع | **الأولوية:** P1

### 2.1 تكامل الجدولة
| المهمة | التفاصيل |
|--------|----------|
| اعتماد `omnexa_projects_pm` | `recommended_apps` في hooks أو تحذير عند غياب WBS |
| ربط BOQ ↔ WBS | حقول `pm_wbs_task` على `BOQ Item` (إن لم تكن موجودة) |
| Baseline Schedule | DocType: `Construction Schedule Baseline` (نسخ تواريخ معتمدة) |

### 2.2 EVM محسّن
**توسيع:** `evm_metrics.py`

| قبل | بعد |
|-----|-----|
| PV خطي من تواريخ العقد | PV من `% إنجاز WBS` أو Baseline |
| EV من BOQ % | EV من QS معتمد + BOQ |
| — | ES، EF، SV، CV، VAC، TCPI |

**تقرير جديد:** `Construction EVM Dashboard` (script + chart)

### 2.3 التزامات مالية (Commitment)
| الميزة | التنفيذ |
|--------|---------|
| Commitment على BOQ | حقول `committed_cost`, `po_committed` rollup |
| Hook | على Submit `Purchase Order` → تحديث BOQ |
| تقرير | `BOQ Commitment vs Actual` |

### 2.4 اختبارات المرحلة 2
- `test_evm_wbs_integration.py`
- `test_boq_commitment.py`

---

## المرحلة 3 — QHSE وأنظمة ISO
**المدة:** 6 أسابيع | **الأولوية:** P1

### 3.1 ISO 9001 — إدارة الجودة
| DocType جديد | الغرض |
|--------------|--------|
| `Construction CAPA` | إجراء تصحيحي/وقائي مرتبط بـ NCR |
| `Construction Internal Audit` | تدقيق داخلي + findings |
| `Construction Quality Audit Finding` | child table |
| `Construction Management Review` | محضر مراجعة إدارة |

**توسيع موجود:**
- `Construction NCR` → Workflow + ربط CAPA
- `Construction Inspection Test Plan` → Hold Points + sign-off

### 3.2 ISO 45001 — السلامة والصحة المهنية
| DocType جديد | الغرض |
|--------------|--------|
| `Construction Hazard Register` | سجل مخاطر |
| `Construction Hazard Register Line` | child |
| `Construction Permit to Work` | تصريح عمل (PTW) |
| `Construction Toolbox Talk` | اجتماع سلامة |
| `Construction Safety KPI` | مؤشرات leading/lagging |

**توسيع:** `Construction HSE Incident` → Workflow تحقيق + إجراءات فورية/جذرية

### 3.3 ISO 14001 — البيئة
| DocType جديد | الغرض |
|--------------|--------|
| `Construction Environmental Aspect` | سجل آثار بيئية |
| `Construction Waste Log` | نفايات/تصريف |
| `Construction Spill Incident` | تسربات (أو توسيع HSE) |
| `Construction Environmental Monitoring` | قياسات (ضوضاء، غبار، مياه) |

### 3.4 Workspace وتقارير QHSE
- Workspace فرعي: **Construction QHSE**
- تقارير: `HSE Incident Summary`, `NCR Aging`, `PTW Register`, `Environmental Compliance`

### 3.5 اختبارات المرحلة 3
- `test_ncr_capa_workflow.py`
- `test_hse_incident.py`
- `test_permit_to_work.py`
- `test_environmental_register.py`

---

## المرحلة 4 — المستندات والتعاون (ISO 19650 + موقع)
**المدة:** 6 أسابيع | **الأولوية:** P1–P2

### 4.1 RFI (طلب معلومات)
| DocType | حقول رئيسية |
|---------|-------------|
| `Construction RFI` | project_contract, subject, question, discipline, due_date, status |
| `Construction RFI Response` | child أو جدول ردود |

**ربط:** Transmittal، CDE، BOQ Item (اختياري)

### 4.2 ISO 19650 — CDE كامل
**توسيع `Construction CDE Document`:**
| الحقل/الميزة | الوصف |
|--------------|--------|
| `naming_convention` | قالب تسمية (مثال: Project-Originator-Type-Number) |
| `suitability_code` | S0–S4 / APM |
| `information_container` | مجلد/حزمة |
| `midp_reference` | رابط خطة تسليم معلومات |
| Validation | server script لفرض التسمية |

| DocType جديد | الغرض |
|--------------|--------|
| `Construction MIDP` | Master Information Delivery Plan |
| `Construction MIDP Line` | مستندات مخططة |

### 4.3 BIM (مرحلة أساسية)
| DocType | الغرض |
|---------|--------|
| `Construction BIM Model Register` | سجل نماذج IFC/RVT |
| `Construction BIM Issue` | BCF-like (موقع، وصف، حالة) |

**ملاحظة:** عارض 3D اختياري (تكامل خارجي أو iframe) — مرحلة 6.

### 4.4 Transmittal متقدم
- مصفوفة اعتماد (من يرسل → من يستلم → إجراء مطلوب)
- مقارنة revision (مرجع CDE supersede موجود — واجهة list)

### 4.5 تحسينات الموقع
| الميزة | DocType/ملف |
|--------|-------------|
| صور على التقرير اليومي | `Site Daily Report` → جدول صور Attach Image |
| موقع GPS | حقول lat/long (اختياري) |
| ربط Material Approval → Stock | عند اعتماد → Material Request |

### 4.6 طباعة عربية/إنجليزية إضافية
- RFI, PTW, NCR, CAPA — قوالب في `construction_forms/print_templates/`

### 4.7 اختبارات المرحلة 4
- `test_construction_rfi.py`
- `test_cde_naming_validation.py`
- `test_document_transmittal.py`

---

## المرحلة 5 — ERP (مخزون، ضرائب، عملات، باطن)
**المدة:** 6 أسابيع | **الأولوية:** P1

### 5.1 المخزون والمواد
| المهمة | التنفيذ |
|--------|---------|
| استهلاك من BOQ BOM | `boq_item_material` → Stock Entry (Material Issue) |
| Hook | Submit `Site Daily Report` → اقتراح/إنشاء Issue |
| تقرير | `Material Consumption vs BOQ` |

**ملف:** `omnexa_construction/inventory_hooks.py`

### 5.2 الضرائب والاستقطاع
| المهمة | التنفيذ |
|--------|---------|
| قالب ضريبة مقاولات | إعدادات على `Project Contract`: vat_template, wht_template |
| IPC + Subcontract Cert | حساب تلقائي + طباعة |
| تكامل SI | `ipc_revenue.py` يمرر taxes |

### 5.3 العملات المتعددة
| المهمة | التنفيذ |
|--------|---------|
| سعر صرف IPC | `exchange_rate` على IPC من تاريخ المستخلص |
| تقرير | revaluation exposure (قراءة من accounting إن وُجد) |

### 5.4 المقاول من الباطن (متقدم)
| الميزة | التنفيذ |
|--------|---------|
| Back-to-back LD | حقول على `Subcontract Work Order` |
| Retention release | `Subcontract Retention Release` DocType |
| Compliance | جدول تأمينات/تراخيص + تنبيه انتهاء |
| Lien waiver | مرفق إلزامي قبل Paid |
| طباعة عربية | `subcontract_payment_certificate_ar.html` |

### 5.5 المشتريات
| المهمة | التنفيذ |
|--------|---------|
| RFQ → Award | زر Create PO من أفضل عرض |
| Prequalification | `Construction Supplier Prequalification` |
| Bid tabulation | تقرير مقارنة عروض |

### 5.6 اختبارات المرحلة 5
- `test_inventory_boq_issue.py`
- `test_ipc_taxes.py`
- `test_subcontract_retention.py`
- `test_rfq_award_po.py`

---

## المرحلة 6 — NEC4، النزاعات، التحليلات، الجوال
**المدة:** 10 أسابيع | **الأولوية:** P2–P3

### 6.1 NEC4
| DocType | الغرض |
|---------|--------|
| `Construction Early Warning` | سجل EW |
| `Construction Compensation Event` | CE numbering + تقييم |
| Programme acceptance | ربط WBS + حالة Accepted/Rejected |

**توسيع `Project Contract`:** when NEC4 → إظهار تبويب NEC

### 6.2 النزاعات (FIDIC Clause 21)
| DocType | الغرض |
|---------|--------|
| `Construction Dispute Case` | قضية/نزاع |
| `Construction Dispute Event` | جدول زمني أحداث |
| `Construction DAB Referral` | إحالة هيئة/decision |
| `Construction Settlement` | تسوية/تحكيم |

### 6.3 BI ولوحة المحفظة
| المخرج | التنفيذ |
|--------|---------|
| Dashboard DocType | `Construction Executive Dashboard` |
| API | `api.py` → portfolio KPIs (عقود، IPC، EVM، QHSE) |
| Charts | Workspace + Number Cards محدثة |

### 6.4 الجوال (اختياري)
- PWA أو Frappe mobile forms لـ Site Daily, PTW, Incident
- Offline queue (تخزين محلي + sync)

### 6.5 تكاملات خارجية (اختياري)
- Webhook لتصدير RFI/Submittal
- مستقبل: Procore/Aconex API adapter في `integrations/`

### 6.6 اختبارات المرحلة 6
- `test_nec4_compensation_event.py`
- `test_dispute_case.py`
- `test_portfolio_api.py`

---

## 4. جدول DocTypes الجديدة (مجموع +22)

| # | DocType | المرحلة |
|---|---------|---------|
| 1 | Construction Snagging Item | 1 |
| 2 | Construction Retention Release | 1 |
| 3 | Construction Change Order BOQ Line | 1 |
| 4 | Construction CAPA | 3 |
| 5 | Construction Internal Audit | 3 |
| 6 | Construction Quality Audit Finding | 3 |
| 7 | Construction Management Review | 3 |
| 8 | Construction Hazard Register | 3 |
| 9 | Construction Hazard Register Line | 3 |
| 10 | Construction Permit to Work | 3 |
| 11 | Construction Toolbox Talk | 3 |
| 12 | Construction Safety KPI | 3 |
| 13 | Construction Environmental Aspect | 3 |
| 14 | Construction Waste Log | 3 |
| 15 | Construction Environmental Monitoring | 3 |
| 16 | Construction RFI | 4 |
| 17 | Construction RFI Response | 4 |
| 18 | Construction MIDP | 4 |
| 19 | Construction MIDP Line | 4 |
| 20 | Construction BIM Model Register | 4 |
| 21 | Construction BIM Issue | 4 |
| 22 | Construction Supplier Prequalification | 5 |
| 23 | Subcontract Retention Release | 5 |
| 24 | Construction Schedule Baseline | 2 |
| 25 | Construction Early Warning | 6 |
| 26 | Construction Compensation Event | 6 |
| 27 | Construction Dispute Case | 6 |
| 28 | Construction Dispute Event | 6 |
| 29 | Construction DAB Referral | 6 |

---

## 5. جدول Workflows المطلوبة

| Workflow | DocType | المرحلة |
|----------|---------|---------|
| IPC Approval | IPC Certificate | 1 |
| Change Order | Construction Change Order | 1 |
| EOT | Construction Extension of Time | 1 |
| Claim | Construction Claim | 1 |
| Final Account | Construction Final Account Statement | 1 |
| Subcontract Payment | Subcontract Payment Certificate | 1 |
| NCR | Construction NCR | 3 |
| CAPA | Construction CAPA | 3 |
| HSE Incident | Construction HSE Incident | 3 |
| PTW | Construction Permit to Work | 3 |
| Material Approval | Construction Material Approval Request | 4 |
| Work Approval | Construction Work Approval Request | 4 |
| RFI | Construction RFI | 4 |

---

## 6. جدول التقارير الجديدة

| التقرير | المرحلة |
|---------|---------|
| Construction FIDIC Compliance | 1 |
| Construction Commercial Pipeline | 1 |
| Construction Snagging Summary | 1 |
| Construction EVM Dashboard | 2 |
| BOQ Commitment vs Actual | 2 |
| HSE Incident Summary | 3 |
| NCR Aging | 3 |
| PTW Register | 3 |
| Environmental Compliance | 3 |
| Material Consumption vs BOQ | 5 |
| RFQ Bid Tabulation | 5 |
| Construction Portfolio Executive | 6 |

---

## 7. i18n وإمكانية الوصول

### 7.1 الترجمة العربية
| المهمة | الملف |
|--------|------|
| استخراج كل labels | `translations/ar.csv` (هدف 500+ سطر) |
| ترجمة Wizard | توسيع `wizard_i18n.js` |
| ترجمة التقارير | `report/*/…json` + `__.py` strings |
| Print EN | نسخ مزدوجة `*_en.html` للنماذج الرئيسية |

### 7.2 إمكانية الوصول (WCAG 2.1 AA — مستوى أساسي)
- `aria-label` على أزرار Wizard
- تباين ألوان في `construction_project_wizard.css`
- دعم لوحة المفاتيح للخطوات 1–8

---

## 8. استراتيجية الاختبارات

### 8.1 هدف التغطية
| منطقة | ملفات اختبار مستهدفة |
|-------|----------------------|
| تجاري | +8 ملفات |
| QHSE | +6 |
| مستندات | +4 |
| ERP hooks | +4 |
| تكامل | +3 E2E |

### 8.2 CI
- تشغيل `bench run-tests --app omnexa_construction` على كل PR
- حد أدنى: لا merge إذا فشلت اختبارات المرحلة الحالية

---

## 9. ترتيب Patches (مقترح)

```
v2_0/
  ensure_construction_specialist_roles.py
  make_commercial_doctypes_submittable.py
  ensure_construction_commercial_workflows.py
  add_ipc_tax_and_ld_fields.py
  ensure_fidic_linkage_fields.py
  ensure_snagging_and_retention_doctypes.py
  ensure_qhse_doctypes.py
  ensure_rfi_and_midp_doctypes.py
  ensure_inventory_hooks.py
  ensure_nec4_and_dispute_doctypes.py
  sync_all_v2_print_formats.py
  update_sap_parity_checklist.py
```

إضافة إلى `patches.txt` تحت قسم `[post_model_sync]` جديد `v2_0`.

---

## 10. المخاطر والتبعيات

| المخاطرة | التخفيف |
|----------|---------|
| غياب `omnexa_projects_pm` | EVM يبقى fallback خطي + تحذير |
| تعقيد Workflow للمستخدمين | قوالب Workflow حسب `governing_standard` |
| تضارب مع engineering_consulting | feature flag `strict_enforce_contract_workflow_binding` |
| نطاق كبير | إصدارات v2.0.1–v2.0.6 كل مرحلة |

---

## 11. تعريف "مكتمل" لكل معيار

### FIDIC (هدف ≥90%)
- [x] IPC Workflow مع اعتماد مهندس
- [x] LD آلي مع سقف
- [x] Time-bar على الإشعارات
- [x] Claim/EOT/CO مرتبطة
- [x] Final Account + Snagging + Retention Release
- [x] تقرير FIDIC Compliance

### PMBOK (هدف ≥80%)
- [x] EVM من WBS/Baseline
- [x] Commitment vs Actual
- [x] Risk (أو ربط PM Risk Register)

### ISO 9001 / 45001 / 14001 (هدف ≥70%)
- [x] CAPA + Internal Audit + Management Review
- [x] Hazard Register + PTW + Toolbox
- [x] Environmental Aspect + Waste Log + Monitoring

### ISO 19650 (هدف ≥60%)
- [x] MIDP + naming validation + transmittal matrix
- [x] BIM Register (بدون عارض 3D إلزامي)

### ERP (هدف ≥85%)
- [x] Stock Issue من BOQ
- [x] VAT/WHT على IPC
- [x] Subcontract متقدم + طباعة AR/EN

---

## 12. الجدول الزمني المرئي (Gantt مبسط)

| المرحلة | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 |
|---------|----|----|----|----|----|----|----|----|----|-----|
| 0 أساس | ██ | ██ | | | | | | | | |
| 1 FIDIC | | ██ | ██ | ██ | | | | | | |
| 2 EVM | | | | ██ | ██ | | | | | |
| 3 QHSE | | | | | ██ | ██ | ██ | | | |
| 4 مستندات | | | | | | ██ | ██ | ██ | | |
| 5 ERP | | | | | | | | ██ | ██ | ██ |
| 6 متقدم | | | | | | | | | ██ | ██ |

---

## 13. الخطوة التالية الفورية (Sprint 1 — أسبوعان)

1. تنفيذ **المرحلة 0** بالكامل (أدوار + submittable + توثيق).  
2. بدء **Workflow IPC** + **LD engine** (أول جزء من المرحلة 1).  
3. تحديث `SAP_PARITY_CHECKLIST.md`.  
4. PR منفصل لكل مرحلة؛ tag إصدار `v2.0.0-alpha` بعد المرحلة 1.

---

## 14. المراجع

- FIDIC 2017 Conditions of Contract (Red/Yellow/Silver Books)  
- PMI PMBOK Guide 7th Edition  
- ISO 19650-1/2 (Organizational & delivery of information)  
- ISO 9001:2015, ISO 45001:2018, ISO 14001:2015  
- NEC4 Engineering and Construction Contract  
- AACE International Recommended Practices (EVM)  
- ErpGenEx internal: `docs/SAP_PARITY_CHECKLIST.md`, تقرير التقييم يونيو 2026  

---

---

## 15. سجل التنفيذ (v2.0 foundation)

| البند | الحالة | ملاحظة |
|-------|--------|--------|
| مرحلة 0 — أدوار متخصصة | ✅ | Patch `ensure_v2_roadmap_foundation` |
| مرحلة 0 — Submittable تجاري | ✅ | 8 DocTypes |
| مرحلة 1 — Workflows | ✅ | 6 workflows |
| مرحلة 1 — LD engine | ✅ | `liquidated_damages.py` |
| مرحلة 1 — FIDIC time-bar | ✅ | `fidic_compliance.py` |
| مرحلة 1 — IPC ضرائب/مهندس | ✅ | Custom fields |
| مرحلة 1 — Snagging / Retention | ✅ | DocTypes جديدة |
| مرحلة 4 — RFI | ✅ | `Construction RFI` |
| مرحلة 3 — CAPA / PTW | ✅ | DocTypes جديدة |
| تقرير FIDIC Compliance | ✅ | Script Report |
| مرحلة 2 — EVM + Commitment | ✅ | `evm_metrics.py`, `boq_commitment.py`, تقرير BOQ Commitment |
| مرحلة 2 — Schedule Baseline | ✅ | `Construction Schedule Baseline` |
| مرحلة 3 — Hazard / ENV / Audit / TBT | ✅ | DocTypes جديدة |
| مرحلة 4 — CDE fields | ✅ | naming, suitability, container |
| مرحلة 5 — Inventory hook | ✅ | `inventory_hooks.py`, زر BOQ |
| مرحلة 4 — MIDP / BIM | ✅ | `Construction MIDP`, BIM Register/Issue |
| مرحلة 4 — CDE validation | ✅ | `cde_validation.py` + hook |
| مرحلة 5 — RFQ → PO | ✅ | `procurement_rfq.py`, حقل PO، زر JS |
| مرحلة 5 — Material Approval → MR | ✅ | `material_approval_hooks.py` |
| مرحلة 5 — IPC exchange_rate | ✅ | `ipc_revenue.py` |
| مرحلة 6 — NEC4 EW / CE | ✅ | Early Warning, Compensation Event |
| مرحلة 6 — نزاعات | ✅ | Dispute Case + Events |
| مرحلة 6 — Portfolio KPIs | ✅ | `portfolio_api.py` |
| طباعة AR إضافية | ✅ | RFI, PTW, NCR, CAPA, Subcontract Payment |
| Patch v2 phase 4–6 | ✅ | `ensure_v2_phase4_5_6` |
| مرحلة 6 — DAB / Settlement | ✅ | DocTypes + ربط Dispute Case |
| مرحلة 5 — Subcontract Retention Release | ✅ | DocType + حساب net_release |
| مرحلة 5 — Material Consumption report | ✅ | `Material Consumption vs BOQ` |
| مرحلة 5 — Site Daily → Stock Entry | ✅ | `site_daily_inventory_hooks.py` |
| مرحلة 6 — NEC4 workflows | ✅ | EW / CE / Dispute workflows |
| مرحلة 6 — Executive Dashboard | ✅ | Page + Number Cards + API |
| Patch v2 phase 6 finalize | ✅ | `ensure_v2_phase6_finalize` |
| مرحلة 5 — Supplier Prequalification | ✅ | DocType + workflow |
| مرحلة 5 — RFQ Bid Tabulation | ✅ | Script Report |
| مرحلة 3 — NCR Aging / PTW Register | ✅ | Script Reports |
| مرحلة 4 — Transmittal revision | ✅ | `transmittal_revision.py` + JS |
| مرحلة 4 — Site Daily GPS/Photos | ✅ | حقول + جدول صور |
| Workflows QHSE/RFI/Prequal | ✅ | `sync_qhse_and_document_workflows` |
| IPC taxes module | ✅ | `ipc_taxes.py` + tests |
| i18n عربي | ✅ | توسيع `translations/ar.csv` (~90 سطر) |
| Patch v2 phase 7 polish | ✅ | `ensure_v2_phase7_polish` |
| Commercial Pipeline report | ✅ | IPC / CO / Claim / EOT / Subcontract |
| Snagging / HSE / ENV reports | ✅ | 3 Script Reports |
| Supplier Prequalification | ✅ | Phase 5 |
| Subcontract compliance + lien waiver | ✅ | Compliance lines + attachment |
| Webhooks / Integrations | ✅ | Settings + doc hooks |
| Site Mobile Hub (PWA shell) | ✅ | Page + service worker |
| IPC print EN | ✅ | `ipc_certificate_en.html` |
| Patch v2 phase 8 closing | ✅ | `ensure_v2_phase8_closing` |
| Management Review / Safety KPI / ENV Monitoring | ✅ | DocTypes ISO |
| Change Order BOQ lines | ✅ | `change_order_boq.py` |
| Transmittal recipients matrix | ✅ | Child table |
| Procore / Aconex adapters | ✅ | `integrations/external_adapters.py` |
| PWA offline queue | ✅ | `mobile_offline.py` + Site Mobile Hub |
| i18n 500+ labels | ✅ | `sync_construction_ar_translations` |
| EN prints RFI/PTW/NCR | ✅ | + IPC EN |
| Construction QHSE workspace | ✅ | Workspace جديد |
| Currency revaluation report | ✅ | Script Report |
| Workflows HSE/Material/Work Approval | ✅ | `sync_qhse_and_document_workflows` |
| Patch v2 final completion | ✅ | `ensure_v2_final_completion` |
| Construction EVM Dashboard | ✅ | Report + chart + summary |
| EN prints Material/Work/CAPA/Subcontract | ✅ | `ensure_v2_roadmap_closure` |
| Roadmap test suite (IPC, BOQ, RFQ, NEC4, QHSE) | ✅ | 12+ test modules |
| Patch v2 roadmap closure | ✅ | `ensure_v2_roadmap_closure` |

*خارطة الطريق v2.0 — **مكتملة**.*

*هذا المستند خطة تنفيذ حية — يُحدَّث عند إغلاق كل مرحلة.*

