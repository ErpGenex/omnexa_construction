# FIDIC Compliance Checklist — omnexa_construction

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Interim Payment Certificate (IPC) | Implemented | `IPC Certificate`, BOQ lines, AR/EN print |
| 2 | IPC submit / workflow | Implemented | `IPC Certificate Approval` workflow + engineer cert fields |
| 3 | Retention & advance recovery | Implemented | `ipc_billing.py`, contract fields |
| 4 | LD / penalties on IPC | Implemented | `liquidated_damages.py`, LD cap on contract |
| 5 | VAT / WHT on IPC | Implemented | `ipc_taxes.py`, custom fields |
| 6 | Variations (Change Orders) | Implemented | `Construction Change Order`, BOQ lines, workflow |
| 7 | EOT | Implemented | `Construction Extension of Time`, workflow, CO link |
| 8 | Claims | Implemented | `Construction Claim`, workflow, CO link |
| 9 | FIDIC Notices + time-bar | Implemented | `fidic_compliance.py`, linked claim/eot/co |
| 10 | Final Account | Implemented | `Construction Final Account Statement` |
| 11 | DLP + Snagging | Implemented | `Construction DLP Record`, `Construction Snagging Item`, open count |
| 12 | Retention Release | Implemented | `Construction Retention Release`, `Subcontract Retention Release` |
| 13 | Dispute / DAB | Implemented | `Construction Dispute Case`, DAB Referral, Settlement |

**Last updated:** v2.0 final completion
