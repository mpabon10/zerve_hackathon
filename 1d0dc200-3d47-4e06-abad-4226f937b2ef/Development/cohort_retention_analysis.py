
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ─────────────────────────────────────────────────────────────────────────────
# MAU COHORT RETENTION ANALYSIS
# Build retention matrix: cohort × months_since_signup
# ─────────────────────────────────────────────────────────────────────────────

# ── Build user × month activity matrix from raw opt_df ──────────────────────
_ts2   = pd.to_datetime(opt_df['timestamp'],  utc=True, errors='coerce')
_pid2  = opt_df['person_id'].astype(str)
_lib2  = opt_df['prop_$lib'].astype(str)

_act_df = pd.DataFrame({
    'person_id': _pid2,
    'ym':        _ts2.dt.to_period('M'),
    'lib':       _lib2,
})

# User → signup cohort (from user_metrics_df)
_cohort_map = user_metrics_df.set_index('person_id')['signup_cohort']

_act_df['cohort'] = _act_df['person_id'].map(_cohort_map)
_act_df = _act_df.dropna(subset=['ym', 'cohort'])

# Unique (person_id, ym) activity
_user_month = _act_df[['person_id', 'ym', 'cohort']].drop_duplicates()
_user_month['ym_dt']     = _user_month['ym'].dt.to_timestamp()
_user_month['cohort_dt'] = pd.PeriodIndex(_user_month['cohort'], freq='M').to_timestamp()
_user_month['months_since_signup'] = (
    (_user_month['ym_dt'].dt.year  - _user_month['cohort_dt'].dt.year) * 12 +
    (_user_month['ym_dt'].dt.month - _user_month['cohort_dt'].dt.month)
)

# Cohort sizes
_cohort_sizes = _user_month[_user_month['months_since_signup'] == 0].groupby('cohort')['person_id'].nunique()

# Pivot: cohort × months_since_signup → n_active_users
_ret_pivot = _user_month.groupby(['cohort', 'months_since_signup'])['person_id'].nunique().unstack(fill_value=0)

# Normalise by cohort size (month-0 users)
_cohort_sizes_aligned = _cohort_sizes.reindex(_ret_pivot.index)
retention_matrix = _ret_pivot.div(_cohort_sizes_aligned, axis=0) * 100  # percentage

# Keep only months 0..4 for clarity
_max_month = min(4, retention_matrix.columns.max())
retention_matrix = retention_matrix[[c for c in retention_matrix.columns if c <= _max_month]]

# ── Month-over-month overall retention (M → M+1) ─────────────────────────────
_months_sorted = sorted(_user_month['ym'].unique())
_mom_data = []
for _m in _months_sorted[:-1]:
    _users_m   = set(_user_month[_user_month['ym'] == _m]['person_id'])
    _users_m1  = set(_user_month[_user_month['ym'] == _months_sorted[_months_sorted.index(_m)+1]]['person_id'])
    _retained  = len(_users_m & _users_m1)
    _mom_data.append({
        'month':          str(_m),
        'active_users':   len(_users_m),
        'retained_next':  _retained,
        'retention_rate': _retained / len(_users_m) * 100 if len(_users_m) > 0 else 0
    })
mom_retention_df = pd.DataFrame(_mom_data)

print("Month-over-Month Retention:")
print(mom_retention_df.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1: Cohort Retention Heatmap
# ─────────────────────────────────────────────────────────────────────────────
BG   = '#1D1D20'
TXT  = '#fbfbff'
STXT = '#909094'

ZERVE_BLUES = ['#1D1D20', '#132236', '#1a3a5c', '#1F77B4', '#A1C9F4']
_cmap = mcolors.LinearSegmentedColormap.from_list('zerve_blues', ZERVE_BLUES, N=256)

fig_retention_heatmap, ax = plt.subplots(figsize=(10, 5))
fig_retention_heatmap.patch.set_facecolor(BG)
ax.set_facecolor(BG)

_data  = retention_matrix.values
_im    = ax.imshow(_data, aspect='auto', cmap=_cmap, vmin=0, vmax=100)

# Labels on cells
for _i in range(_data.shape[0]):
    for _j in range(_data.shape[1]):
        _v = _data[_i, _j]
        _col = TXT if _v < 60 else '#1D1D20'
        ax.text(_j, _i, f'{_v:.0f}%', ha='center', va='center', fontsize=10,
                color=_col, fontweight='bold')

ax.set_xticks(range(len(retention_matrix.columns)))
ax.set_xticklabels([f'Month {c}' for c in retention_matrix.columns], color=TXT, fontsize=10)
ax.set_yticks(range(len(retention_matrix.index)))
ax.set_yticklabels([str(c) for c in retention_matrix.index], color=TXT, fontsize=10)
ax.set_title('Monthly Cohort Retention Heatmap', color=TXT, fontsize=14, fontweight='bold', pad=14)
ax.set_xlabel('Months Since Signup', color=STXT, fontsize=10)
ax.set_ylabel('Signup Cohort', color=STXT, fontsize=10)
ax.tick_params(colors=TXT)
for spine in ax.spines.values():
    spine.set_edgecolor(STXT)

_cb = fig_retention_heatmap.colorbar(_im, ax=ax, pad=0.02)
_cb.ax.yaxis.set_tick_params(color=TXT)
plt.setp(_cb.ax.yaxis.get_ticklabels(), color=TXT)
_cb.set_label('Retention %', color=STXT, fontsize=9)

plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2: Month-over-Month Retention Rate Line Chart
# ─────────────────────────────────────────────────────────────────────────────
fig_mom_retention, ax2 = plt.subplots(figsize=(10, 5))
fig_mom_retention.patch.set_facecolor(BG)
ax2.set_facecolor(BG)

_x = range(len(mom_retention_df))
ax2.plot(list(_x), mom_retention_df['retention_rate'].tolist(), color='#A1C9F4',
         linewidth=2.5, marker='o', markersize=8, markerfacecolor='#ffd400', markeredgecolor='#A1C9F4')
ax2.fill_between(list(_x), mom_retention_df['retention_rate'].tolist(), alpha=0.15, color='#A1C9F4')

# Annotate each point
for _xi, _row in enumerate(mom_retention_df.itertuples()):
    ax2.annotate(f"{_row.retention_rate:.1f}%",
                 xy=(_xi, _row.retention_rate),
                 xytext=(0, 12), textcoords='offset points',
                 ha='center', color=TXT, fontsize=9)

ax2.set_xticks(list(_x))
ax2.set_xticklabels(mom_retention_df['month'].tolist(), color=TXT, fontsize=9, rotation=20)
ax2.set_yticks([0, 25, 50, 75, 100])
ax2.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], color=TXT)
ax2.set_ylim(0, 110)
ax2.set_title('Month-over-Month User Retention Rate', color=TXT, fontsize=14, fontweight='bold', pad=14)
ax2.set_xlabel('Activity Month (→ Retained in Next Month)', color=STXT, fontsize=10)
ax2.set_ylabel('Retention Rate (%)', color=STXT, fontsize=10)
ax2.tick_params(colors=TXT)
ax2.grid(axis='y', color=STXT, alpha=0.2, linestyle='--')
for spine in ax2.spines.values():
    spine.set_edgecolor(STXT)

plt.tight_layout()

print("\nRetention matrix (% of cohort active in each month):")
print(retention_matrix.round(1).to_string())
