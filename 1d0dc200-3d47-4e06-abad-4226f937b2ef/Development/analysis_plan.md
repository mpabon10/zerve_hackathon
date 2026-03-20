# 📊 User Retention & Lifecycle Analysis — Living Spec

> **Dataset**: `zerve_hackathon_for_review.csv`  
> **Shape**: 409,287 events × 104 columns | **Users**: 5,410 `distinct_id` / 4,774 `person_id`  
> **Event types**: 141 unique events | **Date range**: derived from `timestamp` / `created_at`

---

## 🎯 3 Success Metrics

### Metric 1 — **User Activation Rate**
*The % of new users who fire at least one meaningful "work" event (block creation, canvas creation, run_block, agent interaction) within their first 7 days.*

| Property | Value |
|---|---|
| **Why** | 94.8% of rows have a valid `person_id` → we can track every user's first event via `created_at`. High nulls (~80%) on session props confirm most events are programmatic/API, so we need a deliberate activation signal. |
| **Signal events** | `block_create`, `canvas_create`, `run_block`, `agent_message`, `agent_block_run`, `agent_block_created` |
| **Computation** | For each `person_id`: find `min(created_at)` as signup date. Flag `activated = 1` if any signal event fired within `[signup, signup + 7 days]`. Activation Rate = `n_activated / n_total_users`. |
| **Source fields** | `person_id`, `created_at`, `timestamp`, `event` |

---

### Metric 2 — **Monthly Active User (MAU) Retention Rate**
*Month-over-month cohort retention: of users active in month M, what % return in month M+1?*

| Property | Value |
|---|---|
| **Why** | `timestamp` has 386k unique values and zero nulls — a high-resolution activity signal. 141 distinct event types span the full product surface. Cohort analysis directly measures stickiness. |
| **Computation** | Build a `(person_id, year_month)` activity matrix. For each cohort month M, compute `|users_active_M ∩ users_active_M+1| / |users_active_M|`. Report as a cohort retention heatmap. |
| **Source fields** | `person_id`, `timestamp` (parsed to `datetime`), `event` |
| **Exclusions** | Drop system/internal events (`$initialization_time`-only sessions); include all human-facing events. |

---

### Metric 3 — **Feature Adoption Depth Score**
*Per-user count of distinct feature "zones" touched, where zones are derived from event prefixes: `agent_*`, `block_*`, `canvas_*`, `app_*`, `files_*`, `run_*`, `scheduled_job_*`, `source_control_*`.*

| Property | Value |
|---|---|
| **Why** | 141 event types cluster into 8+ feature zones visible in the `event` category column. Depth score correlates with long-term retention and identifies power users vs. casual browsers. |
| **Computation** | For each `person_id`: extract event prefix (before first `_`). Count distinct prefixes → `depth_score ∈ [1..8]`. Segment into: 1 zone = *Explorer*, 2–3 = *Builder*, 4+ = *Power User*. |
| **Source fields** | `person_id`, `event` (category, 141 values), `timestamp` |
| **Credit signal** | Cross-validate with `prop_credits_used` (float32) and `prop_credit_amount` — higher depth should correlate with credit spend. |

---

## 👥 User Segmentation Dimensions

All segments apply across all 3 metrics. Choose one primary + one secondary dimension per analysis pass.

### Primary Dimensions (high signal, low nulls)

| Dimension | Source Column | Cardinality | Null % | Notes |
|---|---|---|---|---|
| **Platform / Lib** | `prop_$lib` | 2 | 0% | `web` vs `python` — the clearest split between web UI users and SDK/API users |
| **Operating System** | `prop_$os` | 6 | 0% | Mac / Windows / Linux / iOS / Android / Other |
| **Device Type** | `prop_$device_type` | 3 | ~79.5% | Desktop / Mobile / Tablet — high nulls but valid for web cohort |
| **Surface / Product Area** | `prop_surface` | low | ~0% | Maps events to product surfaces directly |

### Secondary Dimensions (context-enriching)

| Dimension | Source Column | Cardinality | Null % | Notes |
|---|---|---|---|---|
| **Geography** | `prop_$geoip_country_code` | moderate | ~20% | Country-level; use for regional retention heat maps |
| **Browser** | `prop_$browser` | moderate | ~20% | Chrome / Safari / Firefox — proxy for user context |
| **Python Runtime** | `prop_$python_runtime` | low | high | Relevant only for SDK users (`prop_$lib == 'python'`) |
| **Python Version** | `prop_$python_version` | low | high | Use to understand SDK adoption lifecycle |
| **Tool Name** | `prop_tool_name` | low | high | Links events to specific Zerve tools; use for feature-level segmentation |

### Acquisition / Lifecycle Dimension

| Dimension | Derived From | Notes |
|---|---|---|
| **Signup Cohort (Month)** | `min(created_at)` per `person_id` | Standard cohort grouping for retention curves |
| **User Lifecycle Stage** | Activity recency + depth score | New (<7d) / Active (7–30d) / At-Risk (31–60d) / Churned (>60d) |
| **Activation Status** | Metric 1 output | Activated vs. Not Activated — key churn predictor |

---

## 🔁 Retention & Lifecycle Analytical Approach

### Step 1 — Build User Activity Table
```
user_activity = opt_df.groupby(['person_id', month(timestamp)]).agg(
    n_events = count(event),
    n_event_types = nunique(event),
    n_sessions = nunique(prop_session_id),
    credit_spend = sum(prop_credits_used),
    lib = first(prop_$lib),
    os = first(prop_$os)
)
```
Source columns: `person_id`, `timestamp`, `event`, `prop_session_id`, `prop_credits_used`, `prop_$lib`, `prop_$os`

### Step 2 — Cohort Matrix
- Cohort = `min(timestamp)` month per user
- Activity = any event in each subsequent month
- Output: N×M retention matrix (cohort × months-since-signup)

### Step 3 — Lifecycle Stage Classification
```
days_since_last_event = today - max(timestamp) per person_id
lifecycle_stage:
  - "New"       : days_since_signup <= 7
  - "Active"    : last_event <= 30 days ago
  - "At-Risk"   : last_event 31–60 days ago
  - "Churned"   : last_event > 60 days ago
```

### Step 4 — Per-Segment Metric Computation

For **each combination** of [primary segment] × [lifecycle stage]:
1. **Activation Rate** → `n_activated / n_users` per group
2. **MAU Retention** → month-M-to-M+1 retention rate per cohort × segment
3. **Depth Score** → median and P75 feature zones per segment

---

## 📐 Per-Metric Computation Summary

| Metric | Group By | Aggregation | Output |
|---|---|---|---|
| **Activation Rate** | `signup_cohort`, `prop_$lib`, `prop_$os` | `mean(activated_flag)` | Bar chart by cohort + segment |
| **MAU Retention** | `cohort_month`, `prop_$lib`, `prop_surface` | `retained_users / cohort_size` | Retention heatmap |
| **Feature Depth Score** | `person_id`, then aggregate by segment | `nunique(event_prefix)` → median by group | Box plot / violin chart by lifecycle stage |

---

## 🗂️ Key Field Reference for Python Blocks

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
DEVICE_COL       = 'prop_$device_type'      # 3 values, ~80% null
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

> ⚠️ **Data notes for Python blocks**:
> - `timestamp` and `created_at` are stored as `str` — parse with `pd.to_datetime(..., utc=True)` before any time math
> - `prop_$device_type`, `prop_$browser`, `prop_$geoip_country_code` have ~80% nulls — filter to web cohort (`prop_$lib == 'web'`) before using these
> - `prop_credits_used` / `prop_credit_amount` have high nulls — treat as enrichment, not primary signal
> - Use `person_id` (4,774 unique) as the canonical user key — it has fewer unique values than `distinct_id` (5,410), suggesting some anonymous → identified merging
