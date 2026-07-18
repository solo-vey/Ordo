# Office Readiness & Opening Decision Report

**Company:** {{P01.company_legal_name}}  
**Brand:** {{P02.company_brand_name}}  
**Office:** {{P29.selected_location_address}}  
**Target opening date:** {{P09.target_opening_date}}  
**Final decision:** **{{P50.final_opening_decision}}**

## 1. Executive readiness assessment

The office programme supports the following business objective:

**{{P06.office_business_goal}}**

The programme operates within an initial budget envelope of **{{P10.initial_budget}}** and targets formal opening on **{{P09.target_opening_date}}**.

The selected office received a technical readiness score of **{{P32.technical_readiness_score}}**.

The final readiness decision is:

> **{{P50.final_opening_decision}}**

{{#if P50.final_opening_decision == "conditional open"}}
The report must include a table of opening conditions, owners, deadlines and required evidence.
{{/if}}

{{#if P50.final_opening_decision == "delay"}}
The report must include a recovery plan, revised target date and blocker-resolution path.
{{/if}}

## 2. Facility and delivery readiness

The primary office location is **{{P29.selected_location_address}}**.

The backup location is **{{P30.backup_location_address}}**.

The approved renovation budget is **{{P34.renovation_budget}}**, with fit-out completion planned for **{{P35.fitout_deadline}}**. The primary general contractor is **{{P41.primary_general_contractor}}**.

The delivery programme depends on **{{P42.critical_supplier_count}} critical suppliers**.

The formal readiness test is scheduled for **{{P48.readiness_test_date}}**.

## 3. Technology and security readiness

The office technology and network requirement is:

**{{P36.network_capacity_requirement}}**

**Server room required:** {{P37.server_room_required}}

The required physical-security level is **{{P38.physical_security_level}}**, using the following access-control model:

**{{P39.access_control_model}}**

Technology readiness is owned by **{{P46.local_it_owner}}**. Workplace and facilities readiness are owned by **{{P47.local_facilities_owner}}**.

## 4. People and operating readiness

The office programme targets **{{P43.local_hiring_target}}** and relocation of **{{P44.relocation_target}}**.

The people workstream is owned by **{{P45.local_hr_owner}}**.

**Visa support required:** {{P26.visa_support_required}}

{{#if P26.visa_support_required}}
Outstanding visa cases must be tracked and must not result in employees beginning work without the required legal status.
{{/if}}

## 5. Pilot day result

A pilot working day was conducted with **{{P49.pilot_day_participants}} participants**.

The report must record:

- which office functions were tested;
- which findings were blocking;
- which findings were non-blocking;
- which remediation actions remain open;
- whether the pilot supports the final opening decision.

## 6. Opening conditions and blockers

{{#if P50.final_opening_decision == "conditional open"}}
| Condition | Responsible owner | Deadline | Required evidence | Status |
|---|---|---|---|---|
| {{OPENING_CONDITION_1}} | {{OWNER_1}} | {{DEADLINE_1}} | {{EVIDENCE_1}} | {{STATUS_1}} |
| {{OPENING_CONDITION_2}} | {{OWNER_2}} | {{DEADLINE_2}} | {{EVIDENCE_2}} | {{STATUS_2}} |
{{/if}}

{{#if P50.final_opening_decision == "delay"}}
## Recovery plan

- **Primary blocker:** {{PRIMARY_BLOCKER}}
- **Required remediation:** {{REMEDIATION}}
- **Responsible owner:** {{REMEDIATION_OWNER}}
- **Revised target date:** {{REVISED_OPENING_DATE}}
{{/if}}

## 7. Decision

The opening decision is:

> **{{P50.final_opening_decision}}**

The decision must be interpreted against the readiness-test result, pilot-day findings, supplier dependencies, people readiness, technology readiness and unresolved opening conditions.

## 8. Final package status

This report is the final readiness and decision component of `OFFICE_OPENING_PACKAGE`.

It must be packaged together with:

1. `01_OFFICE_OPENING_BUSINESS_AND_LOCATION_BRIEF.md`
2. `02_OFFICE_BUILD_TECHNOLOGY_AND_OPERATIONS_PLAN.md`
3. `03_OFFICE_READINESS_AND_OPENING_DECISION_REPORT.md`
