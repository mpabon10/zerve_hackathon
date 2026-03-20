# Zerve Activated User Base — Independent Analytical Review

> **Scope:** 409,287 raw events · 4,774 unique users · Signup cohorts Sep–Dec 2025  
> **Activation definition:** Any of `block_create`, `canvas_create`, `run_block`, `agent_message`, `agent_block_run`, or `agent_block_created` within 7 days of signup  
> **Analysis window:** Post-activation behaviour (day 7+) examined across 7 dimensions

---

## Executive Summary

Zerve's activated user base comprises **283 users (5.9% of 4,774 total)**, generating **200,555 post-activation events**. This group is dominated by a small but highly engaged developer cohort — primarily Linux/macOS users operating via the Python SDK — who exhibit strong multi-zone exploration and a tendency to return within days. Activation rates are geographically concentrated and predictable with high accuracy (AUC 0.84), and a clear power-user tier (top decile: 29 users) drives disproportionate platform engagement. Retention remains critically low across all cohorts, with month-2 retention falling below 7% even for the oldest cohort.

---

## §1 — Geography

**4,774 users across 20+ countries; top 3 markets account for 55% of users.**

| Country | Users | Activated | Activation Rate |
|---|---|---|---|
| 🇮🇳 India (IN) | 1,709 (35.8%) | 62 | 3.6% |
| 🇺🇸 USA (US) | 768 (16.1%) | 44 | 5.7% |
| 🇬🇧 UK (GB) | 251 (5.3%) | 15 | 6.0% |
| 🇮🇪 Ireland (IE) | 191 (4.0%) | 23 | **12.0%** |
| 🇫🇷 France (FR) | 65 (1.4%) | 11 | **16.9%** |
| 🇮🇱 Israel (IL) | 26 (0.5%) | 6 | **23.1%** |

**Key insight:** India is Zerve's largest market by volume but has the lowest activation rate among the top 20 countries (3.6%). Smaller Western markets — Israel (23.1%), France (16.9%), Ireland (12.0%) — convert at 3–6× the rate of India. The USA, as the likely primary ICP market, sits at a mid-range 5.7%.

---

## §2 — Post-Activation Event Popularity

**200,555 post-day-7 events from 283 activated users. Top 5 events by volume:**

| Rank | Event | Count | % of Total |
|---|---|---|---|
| 1 | `credits_used` | 96,321 | 48.0% |
| 2 | `addon_credits_used` | 14,445 | 7.2% |
| 3 | `fullscreen_open` | 8,959 | 4.5% |
| 4 | `fullscreen_close` | 8,843 | 4.4% |
| 5 | `run_block` | 8,176 | 4.1% |
| 6 | `agent_tool_call_create_block_tool` | 7,862 | 3.9% |
| 7 | `agent_tool_call_get_block_tool` | 6,410 | 3.2% |

**Key insight:** Credit consumption (`credits_used` + `addon_credits_used`) accounts for **55.2% of all post-activation events**, confirming that activated users are actively running compute. `credits_exceeded` (5,609 events, rank 8) is a warning signal — a meaningful fraction of activated users are hitting credit limits, which is a retention risk. AI agent tool calls (`agent_tool_call_*`) collectively represent ~12% of events, confirming the agent is central to how activated users work.

---

## §3 — Time-to-Activation

**160 activated users with a first activation event within 7 days of signup.**

| Speed Segment | Definition | Users | Share |
|---|---|---|---|
| Fast | ≤ 1 day | 99 | **61.9%** |
| Mid | 1–4 days | 13 | **8.1%** |
| Slow | 4–7 days | 48 | **30.0%** |

**Key insight:** Activation is heavily bimodal — **62% of users who activate do so within their first 24 hours**, then there's a quiet period before a second cluster activates in days 4–7. This U-shaped distribution suggests two distinct user journeys: (1) users who come in with clear intent and activate immediately; (2) users who take time to explore before committing. There is a notable **30% "slow activator" segment** that can likely be accelerated with targeted nudges between days 2–4.

---

## §4 — Engagement Depth

**Activated users explore 3.1× more product zones than non-activated users.**

| Cohort | Median Depth | Mean Depth |
|---|---|---|
| Activated (n=283) | **3.0 zones** | **2.60 zones** |
| Non-activated (n=4,491) | 1.0 zones | 0.83 zones |

Overall depth segment breakdown across all 4,774 users:
- **Explorer (1 zone):** 3,295 users (69.0%)
- **Builder (2–3 zones):** 915 users (19.2%)
- **Power User (4+ zones):** 564 users (11.8%)

Feature zone adoption by activated vs. non-activated users shows `run`, `block`, and `canvas` zones are heavily over-represented in the activated cohort, while `agent` and `source_control` adoption is almost exclusive to activated users.

**Key insight:** Median depth of 1.0 for non-activated users means the majority of signups touch exactly one product zone and leave. The jump from 1 to 3+ zones is the strongest behavioural differentiator between retained and churned users — this is the core engagement threshold Zerve should target in onboarding.

---

## §5 — Session Cadence

**268 activated users have more than one session on record.**

| Metric | Value |
|---|---|
| Median avg inter-session gap | **3.5 days** |
| Mean avg inter-session gap | **6.6 days** |
| Users with >1 session | 268 / 283 (94.7%) |

**Key insight:** The median activated user returns every 3.5 days — closer to twice-weekly than weekly. The mean (6.6 days) is pulled up by a long tail of infrequent returners, suggesting a bifurcated base: daily/every-other-day active users (power users) and weekly-or-less returners. The fact that **94.7% of activated users have more than one session** confirms activation genuinely predicts return behaviour. The `credits_exceeded` event volume (§2) suggests some weekly returners may be session-limited by credit constraints.

---

## §6 — Power Users

**Top decile of activated users (≥ 1,308 events) vs. the regular activated base.**

| Metric | Power Users (n=29) | Regular Activated (n=254) |
|---|---|---|
| Avg total events | **7,149** | 188 |
| Avg depth score | **5.14 zones** | 2.31 zones |
| Avg active months | **3.21 months** | 1.87 months |
| P90 event threshold | **1,308** | — |

**Key insight:** 29 power users (1% of all signups, 10% of activated users) generate a wildly disproportionate share of platform activity — averaging 7,149 events vs. 188 for regular activated users (**38× more events per user**). They cover 5+ of 8 product zones on average and have been active for 3+ months. These users are Zerve's core community and likely provide the most product feedback. Identifying, nurturing, and converting regular activated users into this tier is the highest-leverage growth action.

---

## §7 — Event Sequencing

**First 3 events observed for activated users after day-7 mark.**

| Rank | 1st Event Post-Day-7 | Count |
|---|---|---|
| 1 | `sign_in` | 192 |
| 2 | `link_clicked` | 41 |
| 3 | `credits_used` | 9 |
| 4 | `agent_start_from_prompt` | 8 |
| 5 | `sign_up` | 5 |

Second event most commonly: `sign_in` (79), `agent_new_chat` (26), `canvas_open` (24).  
Third event most commonly: `sign_in` (55), `agent_new_chat` (23), `link_clicked` (22).

**Key insight:** `sign_in` dominates as the first post-activation event (192 of ~283 users, **~68%**), which is expected — users return and authenticate before doing anything. The critical signal is what comes next: `agent_new_chat` appears in positions 2 and 3 at high rates (26 and 23 users), suggesting that **re-engaging with the AI agent is the most common substantive action after a return visit**. The `agent_start_from_prompt` event at position 1 (8 users, ~3%) identifies a high-intent cohort who immediately jump into AI-guided work on return.

---

## Predictive Model Summary

A Lasso logistic regression model trained on the first 7 days of user behaviour predicts post-activation status with **AUC = 0.8376** (excellent discrimination), retaining 7 of 23 features:

| Rank | Feature | Odds Multiplier | Interpretation |
|---|---|---|---|
| 1 | `evt_sign_in` | **1.515×** | Return visits in week 1 are the strongest predictor |
| 2 | `depth_score_7d` | **1.384×** | Multi-zone exploration in week 1 |
| 3 | `plat_web` | **1.223×** | Web platform users (conditional signal) |
| 4 | `agent_tool_call_run_block_tool` | **1.061×** | AI agent block execution |
| 5 | `agent_tool_call_get_canvas_summary_tool` | **1.039×** | Systematic agent canvas exploration |
| 6 | `os_linux` | **1.028×** | Linux = developer demographic |
| 7 | `os_mac_osx` | **1.014×** | macOS = developer/analyst demographic |

The model achieves **86% recall** on the activated class — catching 49 of 57 activated test users. The model is best used as a **day-7 scoring system** to identify high-probability activators for targeted outreach.

---

## Cohort Retention

Month-over-month retention across all signup cohorts is critically low:

| Cohort | Month 0 | Month 1 | Month 2 | Month 3 |
|---|---|---|---|---|
| Sep 2025 | 100% | **9.2%** | 6.5% | 4.8% |
| Oct 2025 | 100% | **4.2%** | 1.9% | 0% |
| Nov 2025 | 100% | **3.9%** | 0% | — |
| Dec 2025 | 100% | **0%** | — | — |

MoM overall retention rates: Sep→Oct **9.2%**, Oct→Nov **11.5%**, Nov→Dec **6.1%**.

**Key insight:** Even the best cohort (Sep 2025) retains fewer than 1 in 10 users in month 2. This is the most urgent metric for Zerve to address. The drop from 100% to <10% in month 1 indicates a severe activation-to-habit gap — users try the product but don't form a return habit.

---

## Prioritised Recommendations

### 🔴 P0 — Address Immediately (Retention Crisis)

**1. Launch a D1/D3/D7 re-engagement sequence for all new signups**  
Month-1 retention is below 10% across all cohorts. A behaviour-triggered email sequence (no activity D1 → nudge, no activation D3 → guided demo, no return D7 → use case prompt) could realistically double month-1 retention. The 62% of fast activators (≤1 day) show intent is there — the product just isn't pulling them back.

**2. Resolve the `credits_exceeded` friction point**  
5,609 `credits_exceeded` events among activated users (rank 8 post-activation) means power users and regular activated users are hitting hard limits. This is a direct retention risk — hitting a wall is a churn trigger. Introduce soft warnings earlier (`credits_below_4` / `credits_below_3` events already captured), add a seamless upgrade path, or consider a credit grace period for new activators.

### 🟠 P1 — High Impact (Activation Rate)

**3. Build a multi-zone discovery experience in onboarding**  
`depth_score_7d` (odds ×1.384) is the second most powerful activation predictor. 69% of users touch only 1 zone. A structured onboarding checklist — "Explore 3 zones to unlock full access" or a guided tour covering canvas → agent → run — would directly target the biggest discriminator between activated and non-activated users. Even moving 10% of Explorers to Builder depth could materially shift the overall activation rate from 5.9%.

**4. Accelerate the "slow activator" segment (days 2–4)**  
30% of activators take 4–7 days — a full 48 users who are "almost there" but haven't committed. A targeted in-product prompt or email at day 2/3 ("You haven't run a block yet — here's a 2-minute demo") could capture a meaningful fraction of this group earlier and reduce dropout in the 1–4 day window.

**5. Make the AI agent the default first action after sign-in**  
Sequencing analysis shows `agent_new_chat` is the most common substantive post-activation action (position 2 and 3). The return-visit funnel should be: sign_in → agent prompt → run something. Consider making the agent chat box the first element visible on return, with a contextual prompt like "Welcome back — pick up where you left off" or "Try asking the agent to analyse your last dataset."

### 🟡 P2 — Segment-Specific Strategies

**6. Create separate onboarding tracks for Python SDK vs. web users**  
Python SDK users activate at **42.2%** vs. web users at **8.2%** — a 5× gap. These are fundamentally different ICPs with different needs. SDK users want technical depth (library docs, code examples, CLI references). Web users need guided discovery (templates, example projects, video walkthroughs). A single onboarding flow is sub-optimal for both.

**7. Prioritise India-specific activation strategies**  
India contributes 35.8% of users (1,709) but only a 3.6% activation rate — the largest absolute untapped pool. Investigate whether this reflects language/localisation gaps, different use cases, or enterprise/student users with different intent. A targeted India-specific content strategy or partner programme could unlock significant activation volume.

**8. Deprioritise mobile activation optimisation**  
iOS users activate at 1.3%, Android at 2.0%. Mobile sessions are evaluative, not building-oriented — users are browsing, not coding. Don't invest in mobile onboarding for activation; instead, use mobile as a top-of-funnel channel that redirects to a desktop sign-up prompt.

**9. Identify and formally recognise the 29 power users**  
29 users averaging 7,149 events and 3+ active months are Zerve's core champions. A power user programme (early feature access, direct feedback channel, community leadership) would (a) retain this critical segment, (b) surface high-quality product feedback, and (c) create social proof for acquisition.

---

*Analysis based on 409,287 raw event records from 4,774 unique users across Sep–Dec 2025 signup cohorts. Predictive model: Lasso logistic regression, AUC 0.8376, trained on 7-day post-signup behaviour window with no data leakage.*
