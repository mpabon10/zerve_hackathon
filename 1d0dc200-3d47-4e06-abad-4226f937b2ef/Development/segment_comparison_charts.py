
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────────────────────────────────────
# SEGMENT COMPARISON: All 3 metrics across key dimensions
# ─────────────────────────────────────────────────────────────────────────────
BG   = '#1D1D20'
TXT  = '#fbfbff'
STXT = '#909094'
PALETTE = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', '#ffd400']

_udf = user_metrics_df.copy()

def _bar_chart(ax, labels, values, title, xlabel, color, fmt='pct'):
    ax.set_facecolor(BG)
    _bars = ax.barh(labels, values, color=color, edgecolor='none', height=0.6)
    for _bar, _v in zip(_bars, values):
        _lbl = f'{_v:.1f}%' if fmt == 'pct' else f'{_v:.1f}'
        ax.text(_bar.get_width() + max(values) * 0.01, _bar.get_y() + _bar.get_height() / 2,
                _lbl, va='center', color=TXT, fontsize=9)
    ax.set_title(title, color=TXT, fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, color=STXT, fontsize=9)
    ax.tick_params(colors=TXT, labelsize=9)
    ax.set_xlim(0, max(values) * 1.2)
    for spine in ax.spines.values():
        spine.set_edgecolor(STXT)
    ax.xaxis.set_tick_params(color=TXT)

# ─────────────────────────────────────────────────────────────────────────────
# CHART A: Activation Rate by Platform (lib)
# ─────────────────────────────────────────────────────────────────────────────
_lib_act = _udf.groupby('lib').agg(
    users=('activated', 'count'),
    activated=('activated', 'sum')
).reset_index()
_lib_act['activation_rate'] = _lib_act['activated'] / _lib_act['users'] * 100
_lib_act = _lib_act.sort_values('activation_rate')

fig_activation_by_platform, ax_a = plt.subplots(figsize=(9, 4))
fig_activation_by_platform.patch.set_facecolor(BG)
_bar_chart(ax_a, _lib_act['lib'].tolist(), _lib_act['activation_rate'].tolist(),
           'Activation Rate by Platform (web vs python)', 'Activation Rate (%)', PALETTE[0])
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART B: Activation Rate by OS
# ─────────────────────────────────────────────────────────────────────────────
_os_act = _udf.groupby('os').agg(
    users=('activated', 'count'),
    activated=('activated', 'sum')
).reset_index()
_os_act = _os_act[_os_act['users'] >= 10]  # min 10 users for validity
_os_act['activation_rate'] = _os_act['activated'] / _os_act['users'] * 100
_os_act = _os_act.sort_values('activation_rate')

fig_activation_by_os, ax_b = plt.subplots(figsize=(9, 5))
fig_activation_by_os.patch.set_facecolor(BG)
_bar_chart(ax_b, _os_act['os'].tolist(), _os_act['activation_rate'].tolist(),
           'Activation Rate by Operating System', 'Activation Rate (%)', PALETTE[1])
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART C: Feature Depth Score by Platform
# ─────────────────────────────────────────────────────────────────────────────
_lib_depth = _udf.groupby(['lib', 'depth_segment']).size().unstack(fill_value=0)
_lib_depth_pct = _lib_depth.div(_lib_depth.sum(axis=1), axis=0) * 100

_seg_order = ['Explorer (1 zone)', 'Builder (2–3 zones)', 'Power User (4+ zones)']
_seg_colors = [PALETTE[0], PALETTE[2], PALETTE[4]]
_seg_order = [s for s in _seg_order if s in _lib_depth_pct.columns]

fig_depth_by_platform, ax_c = plt.subplots(figsize=(9, 4))
fig_depth_by_platform.patch.set_facecolor(BG)
ax_c.set_facecolor(BG)

_bottom = np.zeros(len(_lib_depth_pct))
for _seg, _col in zip(_seg_order, _seg_colors):
    _vals = _lib_depth_pct[_seg].values
    _bars = ax_c.barh(_lib_depth_pct.index.tolist(), _vals, left=_bottom.tolist(),
                      color=_col, edgecolor='none', height=0.5, label=_seg)
    _bottom += _vals

ax_c.set_xlim(0, 100)
ax_c.set_xlabel('% of Users', color=STXT, fontsize=9)
ax_c.set_title('Feature Adoption Depth by Platform', color=TXT, fontsize=11, fontweight='bold', pad=10)
ax_c.tick_params(colors=TXT, labelsize=9)
_leg = ax_c.legend(loc='lower right', framealpha=0, labelcolor=TXT, fontsize=8)
for spine in ax_c.spines.values():
    spine.set_edgecolor(STXT)
plt.tight_layout()


# ─────────────────────────────────────────────────────────────────────────────
# CHART D: Top-10 Countries by Activation Rate (min 5 users)
# ─────────────────────────────────────────────────────────────────────────────
_country_act = _udf.groupby('country').agg(
    users=('activated', 'count'),
    activated=('activated', 'sum')
).reset_index()
_country_act = _country_act[(_country_act['users'] >= 5) & (_country_act['country'] != 'nan')]
_country_act['activation_rate'] = _country_act['activated'] / _country_act['users'] * 100
_top10_countries = _country_act.nlargest(10, 'users').sort_values('activation_rate')

fig_activation_by_country, ax_e = plt.subplots(figsize=(9, 6))
fig_activation_by_country.patch.set_facecolor(BG)
_bar_chart(ax_e, _top10_countries['country'].tolist(),
           _top10_countries['activation_rate'].tolist(),
           'Activation Rate — Top 10 Countries (by Users)', 'Activation Rate (%)', PALETTE[4])
# Add user count labels
for _i, (_v, _u) in enumerate(zip(_top10_countries['activation_rate'].tolist(), _top10_countries['users'].tolist())):
    ax_e.text(0.5, _i, f'n={_u}', va='center', color=STXT, fontsize=8)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART E: Signup Cohort Breakdown — Activation Rate Over Time
# ─────────────────────────────────────────────────────────────────────────────
_cohort_act = _udf.groupby('signup_cohort').agg(
    users=('activated', 'count'),
    activated=('activated', 'sum')
).reset_index().sort_values('signup_cohort')
_cohort_act['activation_rate'] = _cohort_act['activated'] / _cohort_act['users'] * 100

fig_activation_by_cohort, ax_f = plt.subplots(figsize=(9, 4))
fig_activation_by_cohort.patch.set_facecolor(BG)
ax_f.set_facecolor(BG)

_x2 = range(len(_cohort_act))
ax_f.bar(list(_x2), _cohort_act['activation_rate'].tolist(), color=PALETTE[0], edgecolor='none', width=0.5)
for _xi2, _row in enumerate(_cohort_act.itertuples()):
    ax_f.text(_xi2, _row.activation_rate + 0.3,
              f'{_row.activation_rate:.1f}%\n(n={_row.users})', ha='center',
              color=TXT, fontsize=9)

ax_f.set_xticks(list(_x2))
ax_f.set_xticklabels(_cohort_act['signup_cohort'].tolist(), color=TXT, fontsize=9)
ax_f.set_ylabel('Activation Rate (%)', color=STXT, fontsize=9)
ax_f.set_title('7-Day Activation Rate by Signup Cohort', color=TXT, fontsize=11, fontweight='bold', pad=10)
ax_f.tick_params(colors=TXT, labelsize=9)
ax_f.set_ylim(0, _cohort_act['activation_rate'].max() * 1.35)
for spine in ax_f.spines.values():
    spine.set_edgecolor(STXT)
plt.tight_layout()

# ── Print segment comparison tables ─────────────────────────────────────────
print("Activation Rate by Platform:")
print(_lib_act[['lib', 'users', 'activated', 'activation_rate']].to_string(index=False))
print("\nActivation Rate by OS:")
print(_os_act[['os', 'users', 'activated', 'activation_rate']].to_string(index=False))
print("\nActivation Rate by Cohort:")
print(_cohort_act[['signup_cohort', 'users', 'activated', 'activation_rate']].to_string(index=False))
print("\nMedian Depth Score by Lifecycle:")
print(_lc_depth.to_string(index=False))
