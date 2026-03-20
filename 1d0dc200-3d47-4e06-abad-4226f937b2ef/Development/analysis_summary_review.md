# Independent Product Review: Zerve —- User Retention & Lifecycle Analysis

> **Reviewed by an independent analyst** | Dataset: `zerve_hackathon_for_review.csv`
> **Dataset shape**: 409,287 events × 104 columns | **Users**: 4,774 `person_id` / 5,410 `distinct_id`
> **Event types**: 141 unique events | **Date range**: Sep 2025 – Dec 2025

---

## Executive Summary

This review presents a data-driven analysis of Zerve's user base, examining activation rates, monthly retention cohorts, and feature adoption depth across Zerve's registered user population. The analysis is based on telemetry event data exported from the platform and processed independently. Three core success metrics are evaluated, segmented by platform, operating system, geography, and signup cohort.

---

## 1. Dataset & Data Quality

### 1.1 Overview

| Property | Value |
|---|---|
| **Raw shape** | 409,287 rows × 107 columns |
| **Optimised shape** | 409,287 rows × 104 columns |
| **Baseline memory** | 641.1 MB |
| **Optimised memory** | 297.7 MB (−53.6%, saving 343.4 MB) |
| **Columns removed** | 3 (2 high-null >90%, 1 redundant) |
| **Unique users** | 4,774 (`person_id`) / 5,410 (`distinct_id`) |
| **Unique events** | 141 distinct event types |

### 1.2 Data Completeness

The majority of columns carrying web-session metadata (browser, device type, viewport, session recording fields) exhibit approximately 79–88% null rates, consistent with the platform's dual-mode event architecture: ~20.5% of events originate from web UI sessions, and ~79.5% from the Python SDK. This high null rate on web-only fields is expected and does not impair analysis of the core user population.

**Columns with 0% nulls (always present):** `distinct_id`, `person_id`, `created_at`, `uuid`, `event`, `timestamp`, `_inserted_at`, `prop_$lib`, `prop_$os`

### 1.3 dtype Summary (Optimised DataFrame)

| dtype | Column count |
|---|---|
| category | 66 |
| str (object) | 22 |
| float32 | 10 |
| datetime64[us, UTC] | 2 |
| int / other | 4 |

---

## 2. Metric Definitions

### Metric 1 — User Activation Rate

*The percentage of new users who fire at least one meaningful "work" event within their first 7 days.*

| Property | Value |
|---|---|
| **Why** | 94.8% of rows have a valid `person_id`. High nulls (~80%) on session props confirm most events are programmatic/API, so a deliberate activation signal is required. |
| **Signal events** | `block_create`, `canvas_create`, `run_block`, `agent_message`, `agent_block_run`, `agent_block_created` |
| **Computation** | For each `person_id`: find `min(created_at)` as signup date. Flag `activated = 1` if any signal event fired within `[signup, signup + 7 days]`. Activation Rate = `n_activated / n_total_users`. |
| **Source fields** | `person_id`, `created_at`, `timestamp`, `event` |

### Metric 2 — Monthly Active User (MAU) Retention Rate

*Month-over-month cohort retention: of users active in month M, what % return in month M+1?*

| Property | Value |
|---|---|
| **Why** | `timestamp` has 386k unique values and zero nulls — a high-resolution activity signal. 141 distinct event types span the full product surface. Cohort analysis directly measures stickiness. |
| **Computation** | Build a `(person_id, year_month)` activity matrix. For each cohort month M, compute `|users_active_M ∩ users_active_M+1| / |users_active_M|`. |
| **Source fields** | `person_id`, `timestamp`, `event` |

### Metric 3 — Feature Adoption Depth Score

*Per-user count of distinct feature "zones" touched, where zones are derived from event name prefixes.*

| Property | Value |
|---|---|
| **Why** | 141 event types cluster into 8+ feature zones visible in the `event` category column. Depth score correlates with long-term retention and identifies power users vs. casual browsers. |
| **Feature zones** | `agent_*`, `block_*`, `canvas_*`, `app_*`, `files_*`, `run_*`, `scheduled_job_*`, `source_control_*` |
| **Computation** | For each `person_id`: extract event prefix. Count distinct prefixes → `depth_score ∈ [1..8]`. Segment into: 1 zone = *Explorer*, 2–3 = *Builder*, 4+ = *Power User*. |
| **Source fields** | `person_id`, `event`, `timestamp` |

---

## 3. User-Level Results

### 3.1 Overall Summary

| Metric | Value |
|---|---|
| **Total users (person_id)** | 4,774 |
| **Activated users (7-day)** | 743 (15.6%) |

### 3.2 Feature Depth Segment Distribution

| Segment | Users | % of Base |
|---|---|---|
| Explorer (1 zone) | 3,295 | 69.0% |
| Builder (2–3 zones) | 915 | 19.2% |
| Power User (4+ zones) | 564 | 11.8% |

### 3.3 Lifecycle Stage Distribution

| Stage | Users | Definition |
|---|---|---|
| New | 1,434 | Last event ≤ 7 days before reference date |
| Active | 1,430 | Last event 8–30 days before reference date |
| At-Risk | 636 | Last event 31–60 days before reference date |
| Churned | 1,271 | Last event > 60 days before reference date |

### 3.4 Signup Cohort Sizes

| Cohort | Users |
|---|---|
| 2025-09 | 997 |
| 2025-10 | 473 |
| 2025-11 | 2,000 |
| 2025-12 | 1,301 |

> **Note:** The large Nov 2025 cohort (2,000 users) appears to reflect a significant growth event or marketing push, accounting for 41.9% of the analysed user base.

---

## 4. Activation Analysis

### 4.1 Activation Rate by Platform

| Platform | Users | Activated | Activation Rate |
|---|---|---|---|
| web | 3,742 | 307 | 8.2% |
| posthog-python (SDK) | 1,032 | 436 | 42.2% |

**Finding:** SDK/API users activate at a rate more than 5× higher than web UI users (42.2% vs. 8.2%). This is a strong indicator that Zerve's Python SDK users represent a more technically engaged cohort with a clear programmatic use case on day one.

### 4.2 Activation Rate by Operating System

| OS | Users | Activated | Activation Rate |
|---|---|---|---|
| Linux | 1,034 | 450 | 43.5% |
| Mac OS X | 1,139 | 129 | 11.3% |
| Windows | 1,825 | 149 | 8.2% |
| Chrome OS | 41 | 2 | 4.9% |
| Android | 502 | 10 | 2.0% |
| iOS | 233 | 3 | 1.3% |

**Finding:** Linux users — likely developers and data engineers — exhibit the highest activation rate (43.5%), closely aligned with the SDK user profile. Mobile OS users show near-zero activation, suggesting the mobile interface does not currently support meaningful onboarding into core workflows.

### 4.3 Activation Rate by Signup Cohort

| Cohort | Users | Activated | Activation Rate |
|---|---|---|---|
| 2025-09 | 997 | 291 | 29.2% |
| 2025-10 | 473 | 115 | 24.3% |
| 2025-11 | 2,000 | 262 | 13.1% |
| 2025-12 | 1,301 | 75 | 5.8% |

**Finding:** A clear declining trend in activation rate across cohorts is observed. The Sept 2025 cohort activated at nearly 5× the rate of the Dec 2025 cohort. This may reflect a shift in acquisition channel toward less-engaged users, a degradation in onboarding experience, or simply that newer cohorts have not yet had sufficient time to complete activation steps.

---

## 5. Feature Adoption Depth Analysis

### 5.1 Depth Score Distribution

| Depth Score | Users | % of Base |
|---|---|---|
| 1 | 3,295 | 69.0% |
| 2 | 639 | 13.4% |
| 3 | 276 | 5.8% |
| 4 | 269 | 5.6% |
| 5 | 181 | 3.8% |
| 6 | 94 | 2.0% |
| 7 | 16 | 0.3% |
| 8 | 3 | 0.1% |
| 9 | 1 | <0.1% |

### 5.2 Activation Rate by Depth Segment

| Depth Segment | Users | Activated | Activation Rate |
|---|---|---|---|
| Explorer (1 zone) | 3,295 | 2 | 0.1% |
| Builder (2–3 zones) | 915 | 284 | 31.0% |
| Power User (4+ zones) | 564 | 457 | 81.0% |

**Finding:** Feature depth is the single strongest predictor of activation. Power Users activate at 81% — compared to near-zero for single-zone Explorers. This suggests that Zerve's activation signal is tightly coupled with multi-feature engagement: users who explore beyond a single zone are highly likely to complete a meaningful workflow.

### 5.3 Median Credit Spend by Depth Segment (users with >0 credits)

| Depth Segment | Median Credits Used |
|---|---|
| Explorer (1 zone) | 0.014 |
| Builder (2–3 zones) | 1.095 |
| Power User (4+ zones) | 1.622 |

**Finding:** Credit consumption scales with feature engagement depth. Power Users spend ~116× more credits than Explorers (median), validating depth score as a meaningful proxy for platform value consumption and monetisation potential.

---

## 6. MAU Cohort Retention

### 6.1 Month-over-Month Retention Rate

| Activity Month | Active Users | Retained Next Month | Retention Rate |
|---|---|---|---|
| 2025-09 | 997 | 92 | 9.2% |
| 2025-10 | 564 | 65 | 11.5% |
| 2025-11 | 2,084 | 127 | 6.1% |

**Finding:** Month-over-month retention is low across all cohorts, ranging from 6.1% to 11.5%. This is consistent with an early-stage product with rapid user acquisition but not yet a well-established retention loop. The Nov 2025 cohort shows the lowest M→M+1 retention despite the largest absolute cohort size.

### 6.2 Cohort Retention Matrix (% of cohort still active in each subsequent month)

| Signup Cohort | Month 0 | Month 1 | Month 2 | Month 3 |
|---|---|---|---|---|
| 2025-09 | 100.0% | 9.2% | 6.5% | 4.8% |
| 2025-10 | 100.0% | 4.2% | 1.9% | 0.0% |
| 2025-11 | 100.0% | 3.9% | 0.0% | — |
| 2025-12 | 100.0% | 0.0% | — | — |

**Finding:** Retention curves drop sharply after Month 0 across all cohorts. The Sep 2025 cohort — Zerve's earliest in this dataset — shows the highest multi-month retention (4.8% at Month 3), which may reflect early adopter characteristics. The Oct and Nov cohorts show near-zero retention by Month 2–3.

> **Analytical caveat:** Dec 2025 cohort data is limited to a single month of observation at time of analysis. The apparent 0% Month 1 retention for this cohort likely reflects data recency rather than true churn.

---

## 7. Segmentation Framework

### 7.1 Primary Segmentation Dimensions

| Dimension | Source Column | Cardinality | Null % | Notes |
|---|---|---|---|---|
| **Platform / Lib** | `prop_$lib` | 2 | 0% | `web` vs `python` — clearest split between UI and SDK users |
| **Operating System** | `prop_$os` | 6 | 0% | Mac / Windows / Linux / iOS / Android / Other |
| **Device Type** | `prop_$device_type` | 3 | ~79.5% | Desktop / Mobile / Tablet — high nulls but valid for web cohort |
| **Surface / Product Area** | `prop_surface` | low | ~0% | Maps events to product surfaces directly |

### 7.2 Secondary Segmentation Dimensions

| Dimension | Source Column | Cardinality | Null % | Notes |
|---|---|---|---|---|
| **Geography** | `prop_$geoip_country_code` | moderate | ~20% | Country-level; used for regional activation analysis |
| **Browser** | `prop_$browser` | moderate | ~20% | Chrome / Safari / Firefox — proxy for user context |
| **Python Runtime** | `prop_$python_runtime` | low | high | Relevant only for SDK users (`prop_$lib == 'python'`) |
| **Python Version** | `prop_$python_version` | low | high | Used to understand SDK adoption lifecycle |
| **Tool Name** | `prop_tool_name` | low | high | Links events to specific platform tools |

### 7.3 Derived Segmentation Dimensions

| Dimension | Derived From | Notes |
|---|---|---|
| **Signup Cohort (Month)** | `min(created_at)` per `person_id` | Standard cohort grouping for retention curves |
| **User Lifecycle Stage** | Activity recency + depth score | New / Active / At-Risk / Churned |
| **Activation Status** | Metric 1 output | Activated vs. Not Activated — key churn predictor |

---

## 8. Key Field Reference

```python
# Identity
IDENTITY_COLS    = ['person_id', 'distinct_id']

# Time
TIME_COLS        = ['timestamp', 'created_at', '_inserted_at']

# Activity
ACTIVITY_COL     = 'event'                    # category, 141 values
SESSION_COL      = 'prop_session_id'
SURFACE_COL      = 'prop_surface'

# Credits (proxy for value)
CREDIT_SPEND_COL = 'prop_credits_used'        # float32
CREDIT_AMT_COL   = 'prop_credit_amount'       # float32

# Segmentation
LIB_COL          = 'prop_$lib'               # 'web' | 'python'
OS_COL           = 'prop_$os'               # 6 values, 0% null
GEO_COL          = 'prop_$geoip_country_code'
TOOL_COL         = 'prop_tool_name'

# Activation signal events
ACTIVATION_EVENTS = [
    'block_create', 'canvas_create', 'run_block',
    'agent_message', 'agent_block_run', 'agent_block_created'
]

# Feature zones (event prefixes for depth score)
FEATURE_ZONES = ['agent', 'block', 'canvas', 'app', 'files',
                 'run', 'scheduled_job', 'source_control']
```

---

## 9. Data Notes & Methodological Caveats

- `timestamp` and `created_at` are stored as strings — parsed with `pd.to_datetime(..., utc=True)` before any time arithmetic.
- `prop_$device_type`, `prop_$browser`, and `prop_$geoip_country_code` exhibit ~80% null rates — analysis is filtered to the web cohort (`prop_$lib == 'web'`) before using these fields.
- `prop_credits_used` and `prop_credit_amount` carry high null rates — treated as enrichment signals, not primary metrics.
- `person_id` (4,774 unique) is used as the canonical user key — it has fewer unique values than `distinct_id` (5,410), suggesting some anonymous-to-identified identity merging has occurred within the platform.
- The Dec 2025 cohort retention figures should be interpreted cautiously; the dataset was likely extracted before the end of their first full month.

---

## 10. Summary Findings

| Finding | Signal Strength |
|---|---|
| SDK users activate at 5× the rate of web users | ⭐⭐⭐ Strong |
| Feature depth (≥2 zones) is the primary activation predictor | ⭐⭐⭐ Strong |
| Power Users generate ~116× more credit spend than Explorers | ⭐⭐⭐ Strong |
| Cohort activation rates declining sharply (29% → 6% over 4 months) | ⭐⭐ Moderate concern |
| Month-over-month retention is low (6–12%) across all cohorts | ⭐⭐ Moderate concern |
| 69% of users remain single-zone Explorers | ⭐⭐ Opportunity |
| Linux users show disproportionately high activation (43.5%) | ⭐⭐ Signal |
| Mobile users show near-zero activation | ⭐ Informational |
