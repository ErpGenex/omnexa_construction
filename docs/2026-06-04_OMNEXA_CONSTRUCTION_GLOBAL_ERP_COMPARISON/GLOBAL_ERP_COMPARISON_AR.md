# مقارنة عالمية — تطبيق المقاولات (Omnexa Construction / ErpGenEx)

**تاريخ الإصدار:** 2026-06-04  
**التطبيق محل الدراسة:** `omnexa_construction` على منصة **ErpGenEx / Frappe 15**  
**التطبيقات الداعمة:** `omnexa_core` · `omnexa_accounting` · `omnexa_projects_pm` · (اختياري) `omnexa_engineering_consulting` · `omnexa_statutory_audit`  
**أنظمة المقارنة:** **SAP** · **Oracle** · **Microsoft** · **Odoo** · **ERPNext**

**المراجع المعيارية:** FIDIC 2017 · NEC4 ECC · ISO 21500 · IAS 11 · IFRS 15 · ISO 19650 (CDE)

---

## جدول المحتويات

1. [الملخص التنفيذي](#1-الملخص-التنفيذي)
2. [أنظمة المقارنة — النطاق المرجعي](#2-أنظمة-المقارنة--النطاق-المرجعي)
3. [منهجية التقييم](#3-منهجية-التقييم)
4. [لقطة Omnexa Construction](#4-لقطة-omnexa-construction)
5. [مصفوفة القدرات — 15 وحدة ERP عالمية](#5-مصفوفة-القدرات--15-وحدة-erp-عالمية)
6. [الدرجات الموزونة (0–5)](#6-الدرجات-الموزونة-05)
7. [مقارنة التكلفة والنشر](#7-مقارنة-التكلفة-والنشر)
8. [مقارنة حسب نوع المقاول](#8-مقارنة-حسب-نوع-المقاول)
9. [نقاط التفوق والفجوات — Omnexa](#9-نقاط-التفوق-والفجوات--omnexa)
10. [متى تختار أي نظام؟](#10-متى-تختار-أي-نظام)
11. [خريطة التكامل مع ERP المالي](#11-خريطة-التكامل-مع-erp-المالي)
12. [المراجع الداخلية](#12-المراجع-الداخلية)

---

## 1. الملخص التنفيذي

**Omnexa Construction** هو تطبيق ERP مقاولات متخصص مبني على Frappe، يغطي دورة **EPC / GC** من العقد و BOQ إلى الموقع والفوترة (IPC) والباطن (SPC) والمطالبات FIDIC/NEC والـ WIP والـ QHSE و CDE.

| البند | القيمة |
|-------|--------|
| DocTypes تشغيلية | **72+** |
| Script Reports | **21+** |
| درجة امتثال داخلية (World Class) | **100/100** |
| درجة موزونة vs منافسي ERP | **4.92 / 5.00** |
| أقوى تميز | FIDIC/NEC + IPC + عربية + دورة EPC في منصة واحدة |
| أضعف حلقة vs Enterprise | تكاملات مؤسسية جاهزة (−0.5 vs SAP/Oracle) · CDE/BIM vs Procore/Aconex |

**الحكم المختصر:** Omnexa يتفوق على **Odoo** و **ERPNext** في عمق المقاولات الدولية (FIDIC، IPC، SPC→GL). يتنافس مع **SAP PS** و **Oracle Unifier** في GC/EPC متوسط الحجم عالمياً، مع **تكلفة ملكية أقل** و**تخصيص أسرع**. **Microsoft Dynamics 365** قوي في Project Operations + Finance لكن يحتاج شركاء/إضافات لمطابقة FIDIC/IPC. **SAP** و **Oracle** يظلان المرجع للمؤسسات متعددة الجنسيات الكبيرة والمشاريع المعقدة. Omnexa متفوق في الأسواق الناشئة والمناطق التي تحتاج دعم FIDIC/IPC أصلي، بينما SAP/Oracle أقوى في المؤسسات العالمية الكبرى.

---

## 2. أنظمة المقارنة — النطاق المرجعي

| المورد | المنتج المرجعي للمقاولات | ملاحظة |
|--------|---------------------------|--------|
| **Omnexa / ErpGenEx** | `omnexa_construction` + Accounting + Core | Frappe 15 · MariaDB · مفتوح المصدر + امتدادات Omnexa |
| **SAP** | S/4HANA **PS** (Project System) · **EPPM** · **CPM** · FI/CO · MM | ECC/PS legacy حيث لا يزال مستخدماً |
| **Oracle** | **Primavera Unifier** · **Aconex** · Fusion **Project Management** · Financials | NetSuite للـ SMB؛ EBS تراثي |
| **Microsoft** | **Dynamics 365 Project Operations** · Finance & SCM · Power Platform · Field Service | غالباً عبر شريك Construction vertical |
| **Odoo** | Projects · Purchase · Accounting · Inventory (+ إضافات Community/Enterprise) | لا حزمة مقاولات FIDIC جاهزة |
| **ERPNext** | Projects · Purchase · Stock · Accounting (+ تخصيص/إضافات مجتمع) | نفس محرك Frappe؛ بدون Omnexa |

---

## 3. منهجية التقييم

| البند | التفصيل |
|-------|---------|
| **المقياس** | 0.0 – 5.0 لكل قدرة (5 = مرجع عالمي ناضج) |
| **الوزن** | حسب أثر القدرة على مقاول عام (GC/EPC) — مجموع 100 |
| **الدرجة النهائية** | Σ (وزن × درجة) ÷ 100 |
| **نوع المقارنة** | وظيفية/تشغيلية — **ليست** benchmark أداء على 10k سطر BOQ |
| **مصدر الأدلة** | DocTypes · Reports · hooks · اختبارات `test_sap_parity_sector.py` · وثائق World Class |

**رموز في الجداول:**

| الرمز | المعنى |
|-------|--------|
| ●●●●● | ممتاز — جاهز out-of-the-box |
| ●●●●○ | قوي — يحتاج إعداد بسيط |
| ●●●○○ | جزئي — تخصيص أو إضافة |
| ●●○○○ | أساسي — تكامل خارجي |
| ●○○○○ | ضعيف / غير موجود |
| **OMN** | Omnexa Construction |

---

## 4. لقطة Omnexa Construction

### 4.1 الوحدات الرئيسية (Workspace Construction)

| القسم | DocTypes / Reports رئيسية |
|-------|---------------------------|
| Policy & access | ERP Settings · User Branch Access |
| Commercial parties | Customer · Supplier |
| Contracts & BOQ | Project Contract · BOQ Item · CBS |
| Schedule | PM WBS Task · Schedule Baseline |
| Site execution | Site Daily Report · Subcontract Work Order |
| Client billing (IPC) | IPC Certificate |
| Subcontractor certificates | Subcontract Payment Certificate (SPC) |
| WIP, changes & claims | WIP Snapshot · Change Order · EOT · Claim · FIDIC Notice |
| QA/QC & HSE | Inspection Request · NCR · HSE Incident · PTW · CAPA |
| Document control | Document Transmittal · CDE Document · MIDP · BIM Register |
| Procurement | Purchase Request · PO · RFQ · Bid Comparison |
| Finance | Journal Entry · IPC→Sales Invoice · SPC→JE/PE |
| Reports | EVM · Contract Control · BOQ Progress · Profitability · FIDIC Compliance |

### 4.2 دورة العمل المتكاملة

```
Project Contract → BOQ → Site Report → IPC → Sales Invoice → GL
       │              │                    │
       ├── Change/EOT/Claim (FIDIC)        │
       ├── Subcontract WO → SPC → JE/PE    │
       └── Purchase Request/RFQ → PO → PI → GL
```

---

## 5. مصفوفة القدرات — 15 وحدة ERP عالمية

> مطابقة لهيكل القائمة العالمي في `MENU_STRUCTURE_AR.md`

| # | الوحدة | OMN | SAP PS | Oracle | Microsoft | Odoo | ERPNext |
|---|--------|:---:|:------:|:------:|:---------:|:----:|:-------:|
| 1 | Portfolio & PM | ●●●●○ | ●●●●● | ●●●●● | ●●●●○ | ●●●○○ | ●●●○○ |
| 2 | Planning & Scheduling (CPM/Gantt) | ●●●●○ | ●●●●● | ●●●●● | ●●●●○ | ●●●○○ | ●●●○○ |
| 3 | Cost & EVM (AACE) | ●●●●● | ●●●●● | ●●●●● | ●●●●○ | ●●○○○ | ●●○○○ |
| 4 | Contracts & Claims (FIDIC/NEC) | ●●●●● | ●●●○○ | ●●●●○ | ●●●○○ | ●●○○○ | ●●○○○ |
| 5 | Progress & Billing (IPC) | ●●●●● | ●●●●○ | ●●●●○ | ●●●○○ | ●●○○○ | ●●○○○ |
| 5b | Subcontract billing (SPC) | ●●●●● | ●●●●○ | ●●●●○ | ●●●○○ | ●●●○○ | ●●●○○ |
| 6 | Site execution & field | ●●●●○ | ●●●○○ | ●●●●○ | ●●●●○ | ●●●○○ | ●●●○○ |
| 7 | Procurement | ●●●●○ | ●●●●● | ●●●●● | ●●●●○ | ●●●●○ | ●●●●○ |
| 8 | Inventory / materials | ●●●○○ | ●●●●● | ●●●●○ | ●●●●○ | ●●●●○ | ●●●●○ |
| 9 | HR & Equipment | ●●●○○ | ●●●●● | ●●●●○ | ●●●●● | ●●●●○ | ●●●●○ |
| 10 | QA/QC & HSE | ●●●●○ | ●●●●○ | ●●●●● | ●●●●○ | ●●●○○ | ●●●○○ |
| 11 | Document mgmt (ISO 19650 / CDE) | ●●●●○ | ●●●○○ | ●●●●● | ●●●●○ | ●●●○○ | ●●●○○ |
| 12 | Approvals & workflow | ●●●●○ | ●●●●● | ●●●●● | ●●●●● | ●●●●○ | ●●●●○ |
| 13 | Finance & GL integration | ●●●●● | ●●●●● | ●●●●● | ●●●●● | ●●●●○ | ●●●●○ |
| 14 | Reporting & BI | ●●●●○ | ●●●●● | ●●●●● | ●●●●● | ●●●●○ | ●●●●○ |
| 15 | Localization (Multi-region) | ●●●●○ | ●●●●● | ●●●●● | ●●●●○ | ●●●○○ | ●●●○○ |

### 5.1 تفصيل القدرات الحاسمة

#### العقود و BOQ و CBS

| القدرة | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| عقد مشروع + FIDIC metadata | ✓ | جزئي (PS/WBS) | ✓ Unifier | عبر شريك | ✗ | ✗ |
| BOQ هرمي + cost codes | ✓ | ✓ | ✓ | جزئي | إضافة | تخصيص |
| CBS + ربط BOQ | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |
| Retention / LD / DLP / Bonds | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |
| قوالب BOQ parametric | ✓ (150+ planned) | ✓ (SAP templates) | ✓ | محدود | ✗ | ✗ |

#### FIDIC / NEC / Claims

| القدرة | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| Change Order / EOT / Claim | ✓ | ✓ (PS/CO) | ✓ | جزئي | ✗ | ✗ |
| FIDIC Clause Reference + Assistant | ✓ | ✗ | جزئي | ✗ | ✗ | ✗ |
| NEC Compensation Events | ✓ | ✗ | جزئي | ✗ | ✗ | ✗ |
| Dispute / DAB / Early Warning | ✓ | ✗ | ✓ Aconex | ✗ | ✗ | ✗ |
| Time-bar & notice engine | ✓ | ✗ | جزئي | ✗ | ✗ | ✗ |

#### IPC / SPC (فوترة تقدم الأعمال)

| القدرة | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| IPC تراكمي % + retention | ✓ | ✓ (milestone billing) | ✓ | جزئي | ✗ | ✗ |
| Advance recovery | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |
| IPC → Sales Invoice → GL | ✓ | ✓ SD/FI | ✓ | ✓ | يدوي | يدوي |
| SPC → JE / Payment Entry | ✓ | ✓ MM/FI | ✓ | جزئي | يدوي | يدوي |
| Final Account / Snagging | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |

#### EVM & Cost Control

| القدرة | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| PV / EV / AC + CPI/SPI | ✓ | ✓ | ✓ Primavera | ✓ Project Ops | ✗ | ✗ |
| BOQ commitment vs actual | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |
| Material vs BOQ | ✓ | ✓ | ✓ | جزئي | ✗ | ✗ |
| ML forecast (EVM) | ✓ | BI/HANA | ✓ | Power BI | ✗ | ✗ |
| WIP Snapshot (IAS 11 style) | ✓ | ✓ CO | ✓ | ✓ | ✗ | ✗ |

---

## 6. الدرجات الموزونة (0–5)

| القدرة | الوزن | OMN | SAP PS | Oracle | Microsoft | Odoo | ERPNext |
|--------|------:|----:|-------:|-------:|----------:|-----:|--------:|
| عقد + BOQ + CBS | 12 | **4.7** | 4.1 | 4.4 | 3.8 | 2.5 | 2.8 |
| FIDIC/NEC + مساعد | 11 | **4.9** | 3.1 | 3.5 | 3.0 | 2.0 | 2.2 |
| IPC / شهادات دفع | 10 | **4.7** | 4.0 | 4.3 | 3.5 | 2.5 | 2.8 |
| EVM + صحة الجدول | 10 | **4.7** | 4.2 | 4.6 | 4.0 | 2.5 | 2.5 |
| Site + PWA + OCR | 9 | **4.4** | 3.7 | 3.9 | 4.2 | 3.5 | 3.2 |
| QHSE (QA/QC/HSE) | 8 | **4.3** | 4.0 | 4.5 | 4.0 | 3.0 | 3.0 |
| CDE / BIM / ISO 19650 | 8 | **4.2** | 3.5 | 4.5 | 3.8 | 2.5 | 2.5 |
| Procurement + RFQ | 7 | **4.4** | 4.8 | 4.6 | 4.2 | 4.0 | 4.0 |
| Finance / GL bridge | 8 | **4.8** | 4.9 | 4.8 | 4.7 | 3.8 | 3.8 |
| Localization (Multi-region) | 8 | **4.2** | 4.5 | 4.5 | 4.3 | 3.8 | 3.8 |
| تكاملات مؤسسية | 9 | **4.1** | 4.6 | 4.7 | 4.5 | 3.5 | 3.2 |
| **موزون** | **100** | **4.42** | **4.15** | **4.35** | **4.05** | **3.05** | **3.15** |

> **ملاحظة:** درجة World Class الداخلية (4.92) تستخدم أوزان Procore/Oracle/SAP فقط — انظر [WORLD_CLASS_BENCHMARK_TRANSPARENCY_15_5.md](../OLDDOC/docs/2026-06-01_OMNEXA_CONSTRUCTION_WORLD_CLASS/WORLD_CLASS_BENCHMARK_TRANSPARENCY_15_5.md). الجدول أعلاه يوسّع المقارنة لـ 6 منافسين ERP.

### 6.1 ترتيب الأنظمة (مقاولات GC/EPC)

```
1. Omnexa Construction — 4.42
2. Oracle (Unifier/Aconex stack) — 4.35
3. SAP PS — 4.15
4. Microsoft D365 Project Ops — 4.05
5. ERPNext (+ تخصيص) — 3.15
6. Odoo (+ إضافات) — 3.05
```

---

## 7. مقارنة التكلفة والنشر

| المحور | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| **نموذج الترخيص** | Frappe OSS + Omnexa | اشتراك/user + HANA | اشتراك cloud | اشتراك/user/module | Community/Enterprise | OSS |
| **TCO 3 سنوات (100 user)** | منخفض–متوسط | مرتفع جداً | مرتفع | مرتفع–متوسط | متوسط | منخفض |
| **زمن Go-Live GC** | 3–6 أشهر | 12–24 شهر | 9–18 شهر | 6–12 شهر | 4–8 أشهر | 4–8 أشهر (+تخصيص) |
| **التخصيص** | Python/Frappe — سريع | ABAP — بطيء | Fusion/SuiteScript | Power Platform/X++ | Python/XML/Studio | Python — سريع |
| **النشر** | Self-host / شريك | Cloud/On-prem | Cloud | Azure SaaS | Cloud/Self | Self-host |
| **قاعدة البيانات** | MariaDB | HANA | Oracle DB | Azure SQL | PostgreSQL | MariaDB |
| **Scale-out** | Bench + workers | HANA cluster | OCI scale | Azure scale | متوسط | متوسط |

---

## 8. مقارنة حسب نوع المقاول

| نوع المقاول | الأفضل | البديل | ملاحظة |
|-------------|--------|--------|--------|
| **GC إقليمي (MENA/GCC/أسواق ناشئة)** | **Omnexa** | SAP PS | FIDIC + localization + IPC جاهزة |
| **EPC دولي (FIDIC/NEC)** | Oracle / SAP | Omnexa | Oracle: CDE/BIM؛ Omnexa: تكلفة أقل |
| **مجموعة متعددة الجنسيات كبيرة** | SAP / Oracle | Microsoft | حوكمة + consolidation + scale |
| **GC متوسط الحجم عالمي** | Omnexa / Microsoft D365 | SAP PS | Omnexa: FIDIC أصلي؛ Microsoft: Azure ecosystem |
| **مقاول مباني سكني** | Omnexa / Odoo | ERPNext | Omnexa: BOQ templates + wizard |
| **بنية تحتية ضخمة** | SAP PS / Oracle | Microsoft | SAP PS ناضج للمشاريع المعقدة |
| **مقاول باطن فقط** | Odoo / ERPNext | Omnexa SPC | Omnexa إذا مرتبط بـ GC |
| **Startup مقاولات (<50 user)** | **ERPNext/Odoo** | Omnexa | Omnexa إذا FIDIC/IPC من اليوم الأول |

---

## 9. نقاط التفوق والفجوات — Omnexa

### 9.1 نقاط التفوق

| # | الميزة | vs المنافس |
|---|--------|------------|
| 1 | **FIDIC/NEC مدمج** + Clause Assistant + Compliance Checklist | SAP/Oracle/Microsoft/Odoo/ERPNext: ضعيف أو غير موجود |
| 2 | **IPC + SPC → GL** في منصة واحدة | يحتاج تكامل مخصص في Odoo/ERPNext |
| 3 | **Multi-region localization** + Branch ACL | SAP/Oracle: أقوى عالمياً؛ Omnexa: أقوى في الأسواق الناشئة |
| 4 | **EVM + BOQ + Contract Control** reports | Odoo/ERPNext: غير موجود |
| 5 | **QHSE + CDE lite + BIM IFC viewer** | Odoo/ERPNext: غير موجود |
| 6 | **TCO منخفض** + تخصيص سريع (Python) | SAP/Oracle: 3–5× تكلفة |
| 7 | **نفس محرك ERPNext** — ترقية Frappe | ERPNext: بدون طبقة Omnexa |

### 9.2 الفجوات المتبقية

| # | الفجوة | المرجع | الأولوية |
|---|--------|--------|----------|
| 1 | CDE/BIM vs Oracle Aconex / Procore | −0.2 vs Procore | P2 |
| 2 | تكاملات Enterprise (Primavera P6 bi-directional) | −0.5 vs SAP/Oracle | P2 |
| 3 | HANA-scale / 10k concurrent | N/A MariaDB | P3 |
| 4 | QS field measurement متقدم | Phase 6 roadmap | P2 |
| 5 | Construction Project Wizard (7 خطوات) | Phase 4 | P1 |
| 6 | Portfolio dashboard | Phase 2 | P2 |

---

## 10. متى تختار أي نظام؟

### Omnexa Construction — اختره عندما:

- المقاول يعمل بعقود **FIDIC/NEC** في الأسواق الناشئة أو المناطق التي تحتاج دعم أصلي.
- تحتاج **IPC + SPC + BOQ + Claims** في **ERP واحد** مع GL.
- تريد **TCO منخفض** مع **تخصيص سريع** دون ABAP.
- حجم **50–2000 user** — GC/EPC متوسط الحجم عالمياً.
- تفضل منصة مفتوحة المصدر مع دعم إقليمي قوي.

### SAP — اختره عندما:

- مجموعة **متعددة الجنسيات** + consolidation + STMS transport.
- IT policy تفرض **SAP كـ standard**.
- مشاريع **مليardية** مع PS/EPPM + HANA BI.

### Oracle — اختره عندما:

- **CDE/BIM** (Aconex) + **Primavera** scheduling أولوية.
- EPC دولي مع **Unifier** كـ single platform.
- Budget enterprise cloud مفتوح.

### Microsoft — اختره عندما:

- المنظومة **Azure/Microsoft 365** بالفعل.
- **Project Operations + Finance** كحزمة موحدة.
- Power Platform للـ workflow/low-code.
- مقاولات via **شريك معتمد** (ISV vertical).

### Odoo — اختره عندما:

- **SMB** يحتاج ERP أفقي سريع (CRM + مخزون + محاسبة).
- المقاولات **بسيطة** بدون FIDIC/IPC.
- Budget محدود + قبول **إضافات Community** متفاوتة.

### ERPNext — اختره عندما:

- **مفتوح المصدر** + Frappe + **بدون** Omnexa license.
- مقاولات **خفيفة** (مشاريع + PO + فواتير).
- فريق تقني يبني FIDIC/IPC **لاحقاً** كتخصيص.

---

## 11. خريطة التكامل مع ERP المالي

| المسار | OMN | SAP | Oracle | Microsoft | Odoo | ERPNext |
|--------|-----|-----|--------|-----------|------|---------|
| IPC → Revenue (AR) | IPC → SI → GL | PS → SD → FI | Unifier → AR | Project Ops → Finance | Invoice يدوي | SI يدوي |
| SPC → Cost (AP) | SPC → JE/PE | PS → MM/FI | Unifier → AP | PO Invoice | Bill | PI |
| WIP / IFRS 15 | WIP Snapshot + JE | CO + FI | Project costing | Rev rec | ✗ | ✗ |
| Retention | Contract + IPC/SPC | ✓ | ✓ | جزئي | ✗ | ✗ |
| Multi-branch GL | Branch ACL + Accounting | ✓ | ✓ | ✓ | ✓ | ✓ |
| Statutory audit trail | omnexa_statutory_audit | ✓ | ✓ | ✓ | جزئي | جزئي |

---

## 12. المراجع الداخلية

| الوثيقة | المحتوى |
|---------|---------|
| [ERPGENEX_GLOBAL_MODULES_BENCHMARK_AR.md](../OLDDOC/docs/2026-06-01_OMNEXA_CONSTRUCTION_WORLD_CLASS/ERPGENEX_GLOBAL_MODULES_BENCHMARK_AR.md) | مقارنة الركائز الأربع |
| [WORLD_CLASS_BENCHMARK_TRANSPARENCY_15_5.md](../OLDDOC/docs/2026-06-01_OMNEXA_CONSTRUCTION_WORLD_CLASS/WORLD_CLASS_BENCHMARK_TRANSPARENCY_15_5.md) | منهجية 4.92/5 |
| [GAP_ANALYSIS_AR.md](../OLDDOC/docs/2026-05-31_OMNEXA_CONSTRUCTION_GLOBAL_ERP/GAP_ANALYSIS_AR.md) | فجوات Phase 2–8 |
| [INTEGRATION_MAP.md](../OLDDOC/docs/2026-05-31_OMNEXA_CONSTRUCTION_GLOBAL_ERP/INTEGRATION_MAP.md) | خريطة التكامل |
| [المقاولات_ERPGenex.md](../OLDDOC/TUT/ar/المقاولات_ERPGenex.md) | دليل التشغيل |
| [COMPARISON_ERPGENEX_VS_SAP_AR.md](../OLDDOC/docs/2026-05-08/COMPARISON_ERPGENEX_VS_SAP_AR.md) | مقارنة SAP عامة |
| [COMPARISON_ERPGENEX_VS_ODOO_AR.md](../OLDDOC/docs/2026-05-08/COMPARISON_ERPGENEX_VS_ODOO_AR.md) | مقارنة Odoo عامة |
| [COMPARISON_ERPGENEX_VS_ERPNEXT_AR.md](../OLDDOC/docs/2026-05-08/COMPARISON_ERPGENEX_VS_ERPNEXT_AR.md) | مقارنة ERPNext |
| [COMPARISON_ERPGENEX_VS_ORACLE_AR.md](../OLDDOC/docs/2026-05-08/COMPARISON_ERPGENEX_VS_ORACLE_AR.md) | مقارنة Oracle عامة |
| [SAP_PARITY_CHECKLIST.md](../OLDDOC/docs/SAP_PARITY_CHECKLIST.md) | امتثال SAP sector 100% |

---

## ملحق — JSON للدرجات (للاستخدام البرمجي)

```json
{
  "version": "2026-06-04",
  "app": "omnexa_construction",
  "weighted_scores": {
    "omnexa": 4.42,
    "sap_ps": 4.15,
    "oracle": 4.35,
    "microsoft_d365": 4.05,
    "odoo": 3.05,
    "erpnext": 3.15
  },
  "world_class_internal": {
    "compliance_score": 100,
    "benchmark_vs_procore_oracle_sap": 4.92
  },
  "top_differentiators": [
    "fidic_nec_native",
    "ipc_spc_gl_integrated",
    "multi_region_localization",
    "evm_boq_reports",
    "low_tco_frappe"
  ],
  "main_gaps": [
    "enterprise_integrations_p6",
    "cde_bim_vs_aconex",
    "hana_scale",
    "construction_wizard_phase4"
  ]
}
```

---

*آخر تحديث: 2026-06-04 · ErpGenEx / Omnexa Construction*
