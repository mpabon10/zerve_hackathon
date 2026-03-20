# Zerve Platform — User Retention & Lifecycle Analysis
### Independent Analytical Review · Sep–Dec 2025 · 409,287 events · 4,774 users

---

## Metric Definitions

Four metrics frame this entire analysis. All downstream findings trace back to one of these four.

| # | Metric | Definition | Source Fields |
|---|---|---|---|
| **M1** | **User Activation Rate** | % of users who trigger ≥1 meaningful "work" events (`block_create`, `canvas_create`, `run_block`, `agent_message`, `agent_block_run`, `agent_block_created`) within first 7 days of signup | `person_id`, `created_at`, `timestamp`, `event` |
| **M2** | **User Stickiniess Rate** | % of users who triggered an event after first 7 days of signup | `person_id`, `created_at`, `timestamp`, `event` |
| **M3** | **MAU Cohort Retention** | Of users active in month M, what % return in month M+1 (and beyond) | `person_id`, `timestamp` (parsed as datetime UTC) |
| **M4** | **Feature Adoption Depth Score** | Per-user count of distinct product zones touched (zones = event name prefixes: `agent_*`, `block_*`, `canvas_*`, `app_*`, `files_*`, `run_*`, `scheduled_job_*`, `source_control_*`). Segments: Explorer = 1 zone, Builder = 2–3, Power User = 4+ | `person_id`, `event` |

---

## 1. Platform Health: Dataset Overview

| Property | Value |
|---|---|
| Raw shape | 409,287 rows × 107 columns |
| Optimised shape | 409,287 rows × 104 columns (−3 cols: 2 high-null >90%, 1 redundant) |
| Memory: baseline → optimised | 641 MB → 298 MB (−53.6%, saving 343 MB) |
| Unique users (`person_id`) | 4,774 |
| Unique event types | 141 |
| Date range | Sep 2025 – Dec 2025 |

**Dual-mode architecture:** ~79.5% of events originate from the Python SDK; ~20.5% from the web UI. This explains the ~80% null rate on browser/device/session fields — expected and structurally sound. The 9 zero-null fields (`person_id`, `event`, `timestamp`, `created_at`, `prop_$lib`, `prop_$os`, etc.) form a reliable analytical backbone.

**Signup cohort sizes:**

| Cohort | Users | Share |
|---|---|---|
| Sep 2025 | 997 | 20.9% |
| Oct 2025 | 473 | 9.9% |
| Nov 2025 | 2,000 | 41.9% |
| Dec 2025 | 1,301 | 27.3% |

The Nov 2025 cohort is anomalously large — likely a marketing push or growth event — and accounts for 42% of the total analysed user base.

---

## 2. The Activation Crisis

**Overall activation rate: 743 of 4,774 users activated (15.6%).** This is a critical finding — the vast majority of users who sign up never perform a meaningful productive action.

### Time to Activation

| Speed | Definition | Users | Share |
|---|---|---|---|
| Fast | ≤ 1 day | 99 | 61.9% |
| Mid | 1–4 days | 13 | 8.1% |
| Slow | 4–7 days | 48 | 30.0% |

Activation is **bimodal**: 62% activate within 24 hours (high-intent arrivals), then a quiet period before 30% activate in days 4–7. The mid-period (days 1–4) is a conversion gap — only 8.1% activate here, suggesting this is an addressable segment for targeted nudges.

### By Platform

| Platform | Users | Activated | Rate |
|---|---|---|---|
| Python SDK (`posthog-python`) | 1,032 | 436 | **42.2%** |
| Web UI (`web`) | 3,742 | 307 | **8.2%** |

Python SDK users activate at **5× the rate** of web users. SDK users have pre-committed to programmatic use on arrival; web users require guided discovery to reach the same outcome.

### By Operating System

| OS | Users | Activated | Rate |
|---|---|---|---|
| Linux | 1,034 | 450 | **43.5%** |
| Mac OS X | 1,139 | 129 | **11.3%** |
| Windows | 1,825 | 149 | **8.2%** |
| Chrome OS | 41 | 2 | 4.9% |
| Android | 502 | 10 | 2.0% |
| iOS | 233 | 3 | 1.3% |

Linux users — closely aligned with the SDK cohort — lead activation at 43.5%. Mobile users (iOS + Android) activate at <2%, confirming mobile sessions are evaluative, not productive.

### By Signup Cohort

| Cohort | Users | Activated | Rate |
|---|---|---|---|
| Sep 2025 | 997 | 291 | 29.2% |
| Oct 2025 | 473 | 115 | 24.3% |
| Nov 2025 | 2,000 | 262 | 13.1% |
| Dec 2025 | 1,301 | 75 | 5.8% |

**The declining trend is partly a recency artefact:** Dec 2025 cohorts have had less clock time to accumulate post-7-day activity. However, the drop from 29.2% (Sep) to 13.1% (Nov — a cohort with sufficient observation time) is a genuine signal of declining onboarding effectiveness or a shift toward lower-intent acquisition channels.

---

## 3. Feature Adoption Depth: The Structural Differentiator

**69% of all users touch exactly one product zone and leave.**

| Segment | Users | % of Base | Activation Rate | Median Credits Used |
|---|---|---|---|---|
| Explorer (1 zone) | 3,295 | 69.0% | 0.1% | 0.014 |
| Builder (2–3 zones) | 915 | 19.2% | 31.0% | 1.095 |
| Power User (4+ zones) | 564 | 11.8% | 81.0% | 1.622 |

Three findings stand out:

1. **Depth is the clearest behavioural divide.** The jump from Explorer to Builder brings activation from near-zero to 31%; Builder to Power User takes it to 81%.
2. **Credit consumption scales with depth.** Power Users spend ~116× more credits than Explorers (median), validating depth as a proxy for monetisation potential.
3. **Activated users explore 3× more zones.** Activated users: median depth 3.0 zones. Non-activated: median depth 1.0 zones. The `run`, `block`, and `canvas` zones are heavily over-represented in the activated cohort; `agent` and `source_control` are almost exclusive to activated users.

---

## 4. What Predicts Stickiness: Model Findings

A Lasso logistic regression model was trained on the first 7 days of user behaviour to predict if a user will have at least one event 7 days after signup (the user stuck around). The model achieves **AUC = 0.8376** (excellent discrimination) on a held-out test set of 955 users.

| Model | AUC | Features Selected |
|---|---|---|
| **Lasso (L1)** | **0.8376** | **7 / 23** |
| Ridge (L2) | 0.8318 | 23 / 23 |

Lasso is the preferred model: it achieves equivalent discrimination while reducing 23 features to 7 genuine independent signals — directly surfacing the product levers that matter.

**Confusion matrix (Lasso, test set, n=955):** TN=662, FP=236, FN=8, TP=49. Recall = **86%** on the sticky user class — catches 49 of 57 real sticky users. Best used as a day-7 user scoring system, not a hard classifier.

### The 7 Selected Features

| Rank | Feature | Coefficient | Odds Multiplier | Interpretation |
|---|---|---|---|---|
| 1 | `evt_sign_in` | +0.4152 | **1.515×** | Return visits in week 1 = strongest predictor of long-term return |
| 2 | `depth_score_7d` | +0.3251 | **1.384×** | Multi-zone exploration in week 1 |
| 3 | `plat_web` | +0.2014 | **1.223×** | Web users who do engage have a residual platform signal (conditional) |
| 4 | `evt_agent_tool_call_run_block_tool` | +0.0596 | 1.061× | AI agent executes a block — genuine "aha" moment |
| 5 | `evt_agent_tool_call_get_canvas_summary_tool` | +0.0384 | 1.039× | Systematic agent canvas exploration |
| 6 | `os_linux` | +0.0273 | 1.028× | Linux demographic signal (developer) |
| 7 | `os_mac_osx` | +0.0137 | 1.014× | macOS demographic signal |

All 7 selected features are **positive predictors** — driving higher odds of stickiness.

**Key insight on `plat_web` (rank 3):** The raw activation rates favour Python SDK users heavily (42.2% vs 8.2%), but when predicting for stickiness (user comes back to the platform at least 1 week later), web dominates over the 
Python SDK .

### **Core takeaway:**
What drives stickiness is *how often you return* (`sign_in`), *how many different things you try* (`depth`), your *platform and OS context*, and *use of the agent* (`event_agent`). Raw volume of actions doesn't matter independently.

---

## 5. Who Actually Sticks Around: The Sticky User Profile

The 283 sticky users generated **200,555 post-7 Day events** — a 70.8× higher per-user event rate than non-sticky users.


### Session Cadence

Sticky users return every **3.5 days (median)**; mean is 6.6 days, pulled up by a long tail of infrequent returners. **94.7% of sticky users have more than one session**, confirming stickiness genuinely predicts return behaviour.

### Post-7 Day Event Mix

| Rank | Event | Count | Share |
|---|---|---|---|
| 1 | `credits_used` | 96,321 | 48.0% |
| 2 | `addon_credits_used` | 14,445 | 7.2% |
| 3 | `fullscreen_open` | 8,959 | 4.5% |
| 4 | `fullscreen_close` | 8,843 | 4.4% |
| 5 | `run_block` | 8,176 | 4.1% |
| 6 | `agent_tool_call_create_block_tool` | 7,862 | 3.9% |
| 8 | `credits_exceeded` | 5,609 | 2.8% |

Credit events (`credits_used` + `addon_credits_used`) account for **55.2% of all post-7 day activity** — sticky users are actively running compute. AI agent tool calls collectively represent ~12% of events. **`credits_exceeded` (rank 8, 5,609 events) is a retention risk signal**: a meaningful share of sticky users is hitting hard credit limits.

### Return Journey: What Sticky Users Do

First post-day-7 event: `sign_in` (192 users, 68%) — expected. What comes next (Second post-day-7 event) is the signal: `agent_new_chat` appears at both positions 2 (26 users) and 3 (23 users), making **re-engaging with the AI agent the most common substantive action on return**. A small but high-intent cohort of 8 users (~3%) begins with `agent_start_from_prompt` — immediately jumping into AI-guided work.

### Power Users

The top decile of sticky users (≥ 1,308 events, n=29) drives disproportionate platform engagement:

| Metric | Power Users (n=29) | Regular Sticky Users (n=254) | Ratio |
|---|---|---|---|
| Avg total events | **7,149** | 188 | **38×** |
| Avg depth score | **5.14 zones** | 2.31 zones | 2.2× |
| Avg active months | **3.21** | 1.87 | 1.7× |

29 users (1% of all signups) averaging 3+ active months and 5+ product zones represent Zerve's core champion cohort.

### Stickiness By Geography (Top 6 Markets)

| Country | Users | Stuck Around | Rate |
|---|---|---|---|
| 🇮🇳 India (IN) | 1,709 (35.8%) | 62 | 3.6% |
| 🇺🇸 USA (US) | 768 (16.1%) | 44 | 5.7% |
| 🇬🇧 UK (GB) | 251 (5.3%) | 15 | 6.0% |
| 🇮🇪 Ireland (IE) | 191 (4.0%) | 23 | 12.0% |
| 🇫🇷 France (FR) | 65 (1.4%) | 11 | 16.9% |
| 🇮🇱 Israel (IL) | 26 (0.5%) | 6 | 23.1% |

India is Zerve's largest market by volume but has the lowest stickiness rate among major markets (3.6%). Smaller Western markets convert at 3–6× that rate. The USA, as the likely primary ICP market, sits at a mid-range 5.7%.

---

## 6. The Retention Problem

Month-over-month retention is critically low across all cohorts:

| Cohort | Month 0 | Month 1 | Month 2 | Month 3 |
|---|---|---|---|---|
| Sep 2025 | 100.0% | 9.2% | 6.5% | 4.8% |
| Oct 2025 | 100.0% | 4.2% | 1.9% | 0.0% |
| Nov 2025 | 100.0% | 3.9% | 0.0% | — |
| Dec 2025 | 100.0% | 0.0%\* | — | — |

> \* Dec 2025 cohort shows 0% Month-1 retention — likely a data recency artefact rather than true churn; the cohort had not yet completed its first full calendar month at time of extraction.

Even the best cohort (Sep 2025, earliest adopters) retains fewer than 1 in 10 users by Month 2. The drop from 100% to <10% in Month 1 across all cohorts indicates a severe **activation-to-habit gap** — users try the product but do not form a return habit. This is the most urgent metric to address.

**Lifecycle stage snapshot** (reference date at time of analysis):

| Stage | Users | Definition |
|---|---|---|
| New | 1,434 | Last event ≤ 7 days ago |
| Active | 1,430 | Last event 8–30 days ago |
| At-Risk | 636 | Last event 31–60 days ago |
| Churned | 1,271 | Last event > 60 days ago |

26.6% of the user base is already classified as churned. Combined with the 636 at-risk users, over 40% of the base is lost or losing.

---

## 7. Prioritised Recommendations

Recommendations are ranked by estimated impact and directness of traceability to findings.

### P0 — Retention Crisis (Act Immediately)

**1. Launch a D1/D3/D7 re-engagement sequence for all new signups**

*Traceable to: M3 (retention 6–11%), activation bimodal distribution (§5), `evt_sign_in` as strongest predictor (§4)*

Month-1 retention is below 10% across all cohorts. A behaviour-triggered sequence — no activity D1 → nudge, no activation D3 → guided demo, no return D7 → use case prompt — targets both the 62% of fast activators who need a pull-back signal and the 30% slow activators who are primed but haven't committed. This is the single highest-leverage intervention.

**2. Resolve the `credits_exceeded` friction point before it becomes a churn driver**

*Traceable to: `credits_exceeded` at rank 8 as a sticky user predictor (5,609 events); `credits_below_3` / `credits_below_4` events already captured*

Power users and regular activated users are hitting hard credit limits. Introduce progressive soft warnings earlier in the credit spend cycle, add a one-click upgrade path visible at the limit boundary, and consider a grace period for users in their first 30 days of activation.

### P1 — Activation Rate (High Impact)

**3. Build a multi-zone discovery experience in onboarding**

*Traceable to: `depth_score_7d` odds ×1.384 (§4); 69% of users single-zone Explorers (§3); Explorer activation rate 0.1%*

A structured first-week checklist covering canvas, agent, and run zones — tied to a visible progress indicator — directly targets the most powerful behavioural differentiator. Even moving 10% of the 3,295 Explorers to Builder depth (2+ zones) would materially shift the overall 5.9% activation rate.

**4. Accelerate the conversion gap in days 1–4**
*Traceable to: bimodal time-to-activation; only 8.1% of activators activate in days 1–4 (§5)*
An in-product prompt or email at day 2 ("You haven't run a block yet — here's a 2-minute demo") targets the 1–4 day conversion valley where very few users currently commit.

**5. Make the AI agent the default entry point on return visits**

*Traceable to: `agent_new_chat` as most common substantive post-7-day action (§5); `evt_agent_tool_call_run_block_tool` odds ×1.061 (§4)*

The return-visit funnel consistently shows: sign-in → agent prompt → run something. Making the agent chat box the first visible element on return — with a contextual prompt referencing prior canvas state — would shorten the path to the product's highest-value surface.

### P2 — Segment-Specific Strategies

**6. Create separate onboarding tracks for Python SDK vs. web users**

*Traceable to: 42.2% vs 8.2% platform activation gap; `plat_web` positive conditional coefficient (§4)*

These are fundamentally different ICPs. SDK users want technical depth (library docs, CLI references, code examples). Web users need guided discovery (templates, example projects, video walkthroughs). A single onboarding flow under-serves both.

**7. Investigate and address India's activation gap**

*Traceable to: India = 35.8% of users, 3.6% activation rate — lowest of any major market (§5)*

India represents the single largest absolute pool of untapped activation potential (1,709 users, 1,647 not activated). Whether the gap reflects language/localisation barriers, different use cases, or enterprise/student cohorts with different intent requires investigation before investment. A targeted content or partner strategy could unlock significant volume.

**8. Identify and formally recognise the 29 power users**

*Traceable to: power users averaging 7,149 events, 5.14 zones, 3.21 active months (§5)*

These 29 users (1% of all signups) are Zerve's most valuable champions and highest-quality feedback source. A power user programme — early feature access, direct feedback channel, community leadership role — retains this critical segment and creates social proof for acquisition.

**9. Deprioritise mobile activation optimisation**

*Traceable to: iOS 1.3%, Android 2.0% activation rates; `os_android` zeroed by Lasso*

Mobile sessions are evaluative, not productive. Investment in mobile onboarding for activation is unlikely to yield returns. Use mobile as a top-of-funnel channel that redirects users toward a desktop sign-up prompt.

---

## Analytical Caveats

| Caveat | Details |
|---|---|
| **Observational data only** | Model coefficients reflect association, not causation. `sign_in` frequency likely reflects underlying user intent rather than being a directly manipulable lever. Randomised experiments are required to establish causal effects. |
| **Imbalanced target** | Only 5.9% of users stuck around after 7 days. Both models use `class_weight='balanced'`; precision on the positive class is low (17% for Lasso). The model is a scoring/ranking tool, not a hard classifier. |
| **Recency bias in Dec 2025 cohort** | Dec cohort retention and activation figures should be treated as lower bounds; the dataset was likely extracted before this cohort's first full month completed. |
| **Feature vocabulary limited to top 15 events** | The event feature set covers the 15 most frequent event types. Less common but potentially high-signal events (e.g. specific onboarding completion events) are excluded; expanding the feature set may improve AUC. |
| **No session-level or funnel-stage features** | The model operates on aggregate 7-day event counts with no information about session quality, time-to-action, or drop-off points. Funnel-stage features could substantially improve both AUC and actionability. |

---

*Analysis conducted on 409,287 raw event records · 4,774 unique users · Signup cohorts Sep–Dec 2025. Predictive model: Lasso logistic regression (L1, C=0.01, class_weight='balanced', 5-fold stratified CV), AUC 0.8376, trained on 7-day post-signup behaviour window with no data leakage. Feature set: 23 features (17 numeric event/depth, 2 platform OHE, 4 OS OHE). Lasso selected 7/23 features; Ridge retained all 23 (AUC 0.8318).*

# All code cells and markdown summaries below were used to generate this comprehensive report