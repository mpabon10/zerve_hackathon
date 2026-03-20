
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE DEPTH SCORE — Distribution & Cross-validation with Credits
# ─────────────────────────────────────────────────────────────────────────────
BG   = '#1D1D20'
TXT  = '#fbfbff'
STXT = '#909094'
PALETTE = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', '#ffd400']

_udf = user_metrics_df.copy()

# ─────────────────────────────────────────────────────────────────────────────
# CHART A: Depth Score Distribution (bar chart of zone counts)
# ─────────────────────────────────────────────────────────────────────────────
_depth_counts = _udf['depth_score'].value_counts().sort_index()

fig_depth_distribution, ax1 = plt.subplots(figsize=(10, 5))
fig_depth_distribution.patch.set_facecolor(BG)
ax1.set_facecolor(BG)

_bars = ax1.bar(_depth_counts.index.tolist(), _depth_counts.values.tolist(),
                color=PALETTE[0], edgecolor='none', width=0.65)
for _b, _v in zip(_bars, _depth_counts.values.tolist()):
    _pct = _v / len(_udf) * 100
    ax1.text(_b.get_x() + _b.get_width() / 2, _b.get_height() + 8,
             f'{_v:,}\n({_pct:.1f}%)', ha='center', color=TXT, fontsize=9)

# Zone boundary annotations
ax1.axvline(x=1.5, color=STXT, linestyle='--', linewidth=1, alpha=0.5)
ax1.axvline(x=3.5, color=STXT, linestyle='--', linewidth=1, alpha=0.5)
ax1.text(1, _depth_counts.max() * 0.88, 'Explorer', ha='center', color='#A1C9F4', fontsize=9, alpha=0.9)
ax1.text(2.5, _depth_counts.max() * 0.88, 'Builder', ha='center', color='#8DE5A1', fontsize=9, alpha=0.9)
ax1.text(6, _depth_counts.max() * 0.88, 'Power User', ha='center', color='#D0BBFF', fontsize=9, alpha=0.9)

ax1.set_title('Feature Adoption Depth Score Distribution', color=TXT, fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Number of Feature Zones Touched', color=STXT, fontsize=10)
ax1.set_ylabel('Number of Users', color=STXT, fontsize=10)
ax1.tick_params(colors=TXT, labelsize=9)
ax1.set_xticks(_depth_counts.index.tolist())
ax1.set_ylim(0, _depth_counts.max() * 1.2)
for spine in ax1.spines.values():
    spine.set_edgecolor(STXT)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART B: Depth Segment vs Activation Rate (cross-metric view)
# ─────────────────────────────────────────────────────────────────────────────
_depth_act = _udf.groupby('depth_segment').agg(
    users=('activated', 'count'),
    activated=('activated', 'sum')
).reset_index()
_depth_act['activation_rate'] = _depth_act['activated'] / _depth_act['users'] * 100
_seg_order = ['Explorer (1 zone)', 'Builder (2–3 zones)', 'Power User (4+ zones)']
_depth_act['depth_segment'] = pd.Categorical(_depth_act['depth_segment'], categories=_seg_order, ordered=True)
_depth_act = _depth_act.sort_values('depth_segment')

fig_depth_vs_activation, ax2 = plt.subplots(figsize=(9, 4))
fig_depth_vs_activation.patch.set_facecolor(BG)
ax2.set_facecolor(BG)

_seg_colors2 = [PALETTE[0], PALETTE[2], PALETTE[4]]
_bars2 = ax2.bar(_depth_act['depth_segment'].astype(str).tolist(),
                 _depth_act['activation_rate'].tolist(),
                 color=_seg_colors2, edgecolor='none', width=0.45)
for _b, _r in zip(_bars2, _depth_act.itertuples()):
    ax2.text(_b.get_x() + _b.get_width() / 2, _b.get_height() + 0.5,
             f'{_r.activation_rate:.1f}%\n(n={_r.users:,})', ha='center', color=TXT, fontsize=9)

ax2.set_title('Activation Rate by Feature Depth Segment', color=TXT, fontsize=12, fontweight='bold', pad=12)
ax2.set_ylabel('Activation Rate (%)', color=STXT, fontsize=10)
ax2.tick_params(colors=TXT, labelsize=9)
ax2.set_ylim(0, _depth_act['activation_rate'].max() * 1.35)
for spine in ax2.spines.values():
    spine.set_edgecolor(STXT)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART C: Credit spend per depth segment (enrichment correlation)
# ─────────────────────────────────────────────────────────────────────────────
_depth_credits = _udf[_udf['total_credits'] > 0].groupby('depth_segment')['total_credits'].median().reset_index()
_depth_credits['depth_segment'] = pd.Categorical(_depth_credits['depth_segment'], categories=_seg_order, ordered=True)
_depth_credits = _depth_credits.sort_values('depth_segment')

if len(_depth_credits) > 0:
    fig_depth_vs_credits, ax3 = plt.subplots(figsize=(9, 4))
    fig_depth_vs_credits.patch.set_facecolor(BG)
    ax3.set_facecolor(BG)

    _bars3 = ax3.bar(_depth_credits['depth_segment'].astype(str).tolist(),
                     _depth_credits['total_credits'].tolist(),
                     color=[PALETTE[0], PALETTE[2], PALETTE[4]][:len(_depth_credits)],
                     edgecolor='none', width=0.45)
    for _b3, _v3 in zip(_bars3, _depth_credits['total_credits'].tolist()):
        ax3.text(_b3.get_x() + _b3.get_width() / 2, _b3.get_height() + _depth_credits['total_credits'].max() * 0.02,
                 f'{_v3:.1f}', ha='center', color=TXT, fontsize=10, fontweight='bold')

    ax3.set_title('Median Credit Spend by Feature Depth Segment', color=TXT, fontsize=12, fontweight='bold', pad=12)
    ax3.set_ylabel('Median Credits Used', color=STXT, fontsize=10)
    ax3.tick_params(colors=TXT, labelsize=9)
    ax3.set_ylim(0, _depth_credits['total_credits'].max() * 1.3)
    for spine in ax3.spines.values():
        spine.set_edgecolor(STXT)
    plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# CHART D: Activated vs Non-Activated — Depth Score Comparison
# ─────────────────────────────────────────────────────────────────────────────
_act_depth = _udf.groupby('activated')['depth_score'].value_counts().unstack(fill_value=0)
_act_depth_pct = _act_depth.div(_act_depth.sum(axis=1), axis=0) * 100
_act_depth_pct.index = ['Not Activated', 'Activated']

fig_activated_vs_depth, ax4 = plt.subplots(figsize=(9, 4))
fig_activated_vs_depth.patch.set_facecolor(BG)
ax4.set_facecolor(BG)

_x_pos = np.array(range(len(_act_depth_pct.columns)))
_width = 0.35
_bars_na = ax4.bar(_x_pos - _width / 2, _act_depth_pct.loc['Not Activated'].values.tolist(),
                   width=_width, color=PALETTE[3], edgecolor='none', label='Not Activated', alpha=0.9)
_bars_a  = ax4.bar(_x_pos + _width / 2, _act_depth_pct.loc['Activated'].values.tolist(),
                   width=_width, color=PALETTE[2], edgecolor='none', label='Activated', alpha=0.9)

ax4.set_xticks(_x_pos.tolist())
ax4.set_xticklabels([f'Zone {c}' for c in _act_depth_pct.columns], color=TXT, fontsize=9)
ax4.set_title('Depth Score: Activated vs Non-Activated Users', color=TXT, fontsize=12, fontweight='bold', pad=12)
ax4.set_ylabel('% of Users', color=STXT, fontsize=10)
ax4.tick_params(colors=TXT, labelsize=9)
ax4.legend(framealpha=0, labelcolor=TXT, fontsize=9)
for spine in ax4.spines.values():
    spine.set_edgecolor(STXT)
plt.tight_layout()

# ── Print summary tables ─────────────────────────────────────────────────────
print("Depth Score Distribution:")
print(pd.DataFrame({'depth_score': _depth_counts.index, 'users': _depth_counts.values}).to_string(index=False))
print("\nActivation Rate by Depth Segment:")
print(_depth_act[['depth_segment', 'users', 'activated', 'activation_rate']].to_string(index=False))
if len(_depth_credits) > 0:
    print("\nMedian Credits by Depth Segment (users with >0 credits):")
    print(_depth_credits.to_string(index=False))
