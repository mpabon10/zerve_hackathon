
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
_BG   = '#1D1D20'
_TXT  = '#fbfbff'
_STXT = '#909094'
_C1   = '#A1C9F4'
_C2   = '#FFB482'
_C3   = '#8DE5A1'
_C4   = '#FF9F9B'
_C5   = '#D0BBFF'
_C6   = '#ffd400'
_PAL  = [_C1, _C2, _C3, _C4, _C5, _C6, '#17b26a', '#f04438']

def _sty(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_STXT, labelsize=9)
    ax.xaxis.label.set_color(_STXT)
    ax.yaxis.label.set_color(_STXT)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if title:
        ax.set_title(title, color=_TXT, fontsize=13, fontweight='bold', pad=10)
    for _sp in ax.spines.values():
        _sp.set_edgecolor('#3a3a3d')
    ax.grid(axis='y', color='#3a3a3d', linewidth=0.5, alpha=0.6)

def _newfig(w=12, h=6):
    _f = plt.figure(figsize=(w, h), facecolor=_BG)
    _a = _f.add_subplot(111)
    _a.set_facecolor(_BG)
    return _f, _a

_ACT_EVS = ['block_create', 'canvas_create', 'run_block',
             'agent_message', 'agent_block_run', 'agent_block_created']
_ZONES   = ['agent', 'block', 'canvas', 'app', 'files', 'run', 'scheduled_job', 'source_control']

# ─────────────────────────────────────────────────────────────────────────────
# BUILD EVENT-LEVEL WORKING TABLE FROM opt_df
# ─────────────────────────────────────────────────────────────────────────────
_ts_w   = pd.to_datetime(opt_df['timestamp'],  utc=True, errors='coerce')
_cat_w  = pd.to_datetime(opt_df['created_at'], utc=True, errors='coerce')
_sess_c = 'prop_$session_id' if 'prop_$session_id' in opt_df.columns else 'prop_session_id'

_evw = pd.DataFrame({
    'person_id': opt_df['person_id'].astype(str),
    'event'    : opt_df['event'].astype(str),
    'timestamp': _ts_w,
    'created_at': _cat_w,
    'country'  : opt_df['prop_$geoip_country_code'].astype(str),
    'sess_id'  : opt_df[_sess_c].astype(str),
})

_sig_dt = _evw.groupby('person_id')['created_at'].min().rename('signup_dt')
_evw    = _evw.merge(_sig_dt, on='person_id')
_evw['days_from_signup'] = (_evw['timestamp'] - _evw['signup_dt']).dt.total_seconds() / 86400.0

# Activated cohort: use ml_dataset_7d's activated_post7d flag (authoritative ground truth)
_actset = set(ml_dataset_7d[ml_dataset_7d['activated_post7d'] == 1]['person_id'].astype(str))

_evw['is_activated'] = _evw['person_id'].isin(_actset)
_act_all = _evw[_evw['is_activated']].copy()
_post7   = _act_all[_act_all['days_from_signup'] > 7].copy()

_total_users = _evw['person_id'].nunique()
print(f"Total users            : {_total_users:,}")
print(f"Activated users (7-day): {len(_actset):,}  ({len(_actset)/_total_users*100:.1f}%)")
print(f"Post-7d events (act.)  : {len(_post7):,}")

# ─────────────────────────────────────────────────────────────────────────────
# BUILD MINI USER METRICS from ml_dataset_7d + opt_df
# (replaces user_metrics_df since it's not in scope from extract_lasso_coefficients chain)
# ─────────────────────────────────────────────────────────────────────────────
_user_ev_cnt = _evw.groupby('person_id').size().rename('total_events')
_user_first  = _evw.groupby('person_id')['timestamp'].min().rename('first_seen')
_user_last   = _evw.groupby('person_id')['timestamp'].max().rename('last_seen')

def _zone_of(e):
    for _z in _ZONES:
        if e.startswith(_z):
            return _z
    return 'other'

_evw['zone'] = _evw['event'].map(_zone_of)
_user_depth = _evw[_evw['zone'] != 'other'].groupby('person_id')['zone'].nunique().rename('depth_score')
_user_months = (
    _evw.assign(ym=_evw['timestamp'].dt.to_period('M'))
    .groupby('person_id')['ym'].nunique().rename('active_months')
)

_umet = pd.DataFrame({
    'total_events' : _user_ev_cnt,
    'first_seen'   : _user_first,
    'last_seen'    : _user_last,
    'active_months': _user_months,
}).reset_index()
_umet['depth_score']     = _umet['person_id'].map(_user_depth).fillna(0).astype(int)
_umet['activated']       = _umet['person_id'].isin(_actset).astype(int)
_umet['days_active_span'] = (_umet['last_seen'] - _umet['first_seen']).dt.total_seconds() / 86400.0

print(f"\nUser metrics built: {len(_umet):,} users")

# ─────────────────────────────────────────────────────────────────────────────
# §1  GEOGRAPHY BREAKDOWN
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §1  GEOGRAPHY BREAKDOWN")
print("="*60)

_geo_u = _evw.drop_duplicates('person_id')[['person_id','country','is_activated']]
_geo_u = _geo_u[~_geo_u['country'].isin(['nan','None',''])]
_geo_g = _geo_u.groupby('country').agg(
    total_users   = ('person_id','count'),
    activated_cnt = ('is_activated','sum')
).reset_index()
_geo_g['activation_rate'] = _geo_g['activated_cnt'] / _geo_g['total_users'] * 100
_geo20 = _geo_g.sort_values('total_users', ascending=False).head(20)
print(_geo20[['country','total_users','activated_cnt','activation_rate']].to_string(index=False))

fig_geo, ax_geo = _newfig(14, 7)
_gcols = [_C1 if r >= _geo20['activation_rate'].median() else _C4 for r in _geo20['activation_rate']]
ax_geo.bar(_geo20['country'], _geo20['total_users'], color=_gcols, edgecolor='none', zorder=3)
_ax2g = ax_geo.twinx()
_ax2g.plot(_geo20['country'], _geo20['activation_rate'], color=_C6, linewidth=2, marker='o', markersize=5, zorder=4)
_ax2g.set_ylabel('Activation Rate (%)', color=_C6, fontsize=10)
_ax2g.tick_params(colors=_C6, labelsize=9)
_ax2g.set_facecolor(_BG)
for _sn, _sv in _ax2g.spines.items():
    _sv.set_edgecolor(_C6 if _sn == 'right' else '#3a3a3d')
_sty(ax_geo, title='§1  Geography: Top 20 Countries — User Volume & Activation Rate',
     xlabel='Country Code', ylabel='User Count')
ax_geo.tick_params(axis='x', rotation=45)
ax_geo.grid(axis='y', color='#3a3a3d', linewidth=0.5, alpha=0.6, zorder=0)
from matplotlib.patches import Patch as _Patch
ax_geo.legend(handles=[
    _Patch(facecolor=_C1, label='≥ median activation rate'),
    _Patch(facecolor=_C4, label='< median activation rate'),
    plt.Line2D([0],[0], color=_C6, linewidth=2, marker='o', label='Activation rate (%)'),
], loc='upper right', facecolor='#2a2a2d', edgecolor='#3a3a3d', labelcolor=_TXT, fontsize=9)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §2  POST-ACTIVATION EVENT POPULARITY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §2  POST-ACTIVATION EVENT POPULARITY")
print("="*60)

_pa_evc = _post7['event'].value_counts().head(25)
print(_pa_evc.to_string())

fig_evpop, ax_evpop = _newfig(14, 8)
_evn  = [e.replace('_', ' ') for e in _pa_evc.index]
_evv  = _pa_evc.values
ax_evpop.barh(range(len(_evn)), _evv, color=[_PAL[i % len(_PAL)] for i in range(len(_evv))], edgecolor='none', zorder=3)
ax_evpop.set_yticks(range(len(_evn)))
ax_evpop.set_yticklabels(_evn, fontsize=9, color=_TXT)
ax_evpop.invert_yaxis()
for _i2, _v2 in enumerate(_evv):
    ax_evpop.text(_v2 + _evv[0]*0.005, _i2, f'{_v2:,}', va='center', ha='left', color=_STXT, fontsize=8)
_sty(ax_evpop, title='§2  Post-Activation Event Popularity — Top 25 Events (after day 7)',
     xlabel='Event Count', ylabel='')
ax_evpop.grid(axis='x', color='#3a3a3d', linewidth=0.5, alpha=0.6, zorder=0)
ax_evpop.grid(axis='y', visible=False)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §3  TIME-TO-ACTIVATION DISTRIBUTION
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §3  TIME-TO-ACTIVATION DISTRIBUTION")
print("="*60)

_act_ev  = _evw[_evw['event'].isin(_ACT_EVS)].copy()
_first_act = (
    _act_ev[_act_ev['person_id'].isin(_actset)]
    .groupby('person_id')['days_from_signup']
    .min().reset_index(name='days_to_act')
)
_first_act['days_to_act'] = _first_act['days_to_act'].clip(lower=0, upper=7)
_nfast = (_first_act['days_to_act'] <= 1).sum()
_nmid  = ((_first_act['days_to_act'] > 1) & (_first_act['days_to_act'] <= 4)).sum()
_nslow = (_first_act['days_to_act'] > 4).sum()
_ntot  = len(_first_act)
print(f"Fast  ≤1d  : {_nfast:,}  ({_nfast/_ntot*100:.1f}%)")
print(f"Mid   1-4d : {_nmid:,}  ({_nmid/_ntot*100:.1f}%)")
print(f"Slow  >4d  : {_nslow:,}  ({_nslow/_ntot*100:.1f}%)")

fig_tta, ax_tta = _newfig(12, 6)
_bins3 = np.arange(0, 8.5, 0.5)
_nh, _edg, _ptch = ax_tta.hist(_first_act['days_to_act'], bins=_bins3,
                                 color=_C1, edgecolor=_BG, linewidth=0.5, zorder=3)
for _p3, _el in zip(_ptch, _edg[:-1]):
    _p3.set_facecolor(_C3 if _el <= 1 else (_C2 if _el <= 4 else _C4))
ax_tta.legend(handles=[
    _Patch(facecolor=_C3, label=f'Fast ≤1d ({_nfast:,})'),
    _Patch(facecolor=_C2, label=f'Mid 1–4d ({_nmid:,})'),
    _Patch(facecolor=_C4, label=f'Slow >4d ({_nslow:,})'),
], facecolor='#2a2a2d', edgecolor='#3a3a3d', labelcolor=_TXT, fontsize=9)
_sty(ax_tta, title='§3  Time-to-Activation — Days from Signup to First Activation Event',
     xlabel='Days from Signup', ylabel='Number of Users')
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §4  ENGAGEMENT DEPTH — activated vs non-activated (from built metrics)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §4  POST-ACTIVATION ENGAGEMENT DEPTH")
print("="*60)

_ad = _umet[_umet['activated'] == 1]['depth_score']
_nd = _umet[_umet['activated'] == 0]['depth_score']
print(f"Activated   — median depth: {_ad.median():.1f}  mean: {_ad.mean():.2f}")
print(f"Non-activated — median depth: {_nd.median():.1f}  mean: {_nd.mean():.2f}")

_zpu = _evw[_evw['zone'] != 'other'].groupby(['person_id','zone']).size().reset_index(name='cnt')
_zpu = _zpu.merge(_umet[['person_id','activated']], on='person_id')
_za  = _zpu[_zpu['activated'] == 1]
_zn  = _zpu[_zpu['activated'] == 0]
_nau = _umet[_umet['activated'] == 1]['person_id'].nunique()
_nnu = _umet[_umet['activated'] == 0]['person_id'].nunique()
_zsa = _za.groupby('zone')['person_id'].nunique() / _nau * 100
_zsn = _zn.groupby('zone')['person_id'].nunique() / _nnu * 100
_zdf = pd.DataFrame({'Activated': _zsa, 'Non-Activated': _zsn}).fillna(0)
_zdf = _zdf.sort_values('Activated', ascending=False)

fig_depth, ax_depth = _newfig(14, 6)
_xz = np.arange(len(_zdf))
_wz = 0.38
ax_depth.bar(_xz - _wz/2, _zdf['Activated'],     width=_wz, color=_C3, label='Activated',     edgecolor='none', zorder=3)
ax_depth.bar(_xz + _wz/2, _zdf['Non-Activated'], width=_wz, color=_C4, label='Non-Activated', edgecolor='none', zorder=3)
ax_depth.set_xticks(_xz)
ax_depth.set_xticklabels(_zdf.index, rotation=30, ha='right', fontsize=9, color=_TXT)
ax_depth.legend(facecolor='#2a2a2d', edgecolor='#3a3a3d', labelcolor=_TXT, fontsize=9)
_sty(ax_depth, title='§4  Feature Zone Breadth — Activated vs Non-Activated (% of cohort)',
     xlabel='Feature Zone', ylabel='% of Users in Cohort')
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §5  SESSION CADENCE
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §5  SESSION CADENCE (Activated Users)")
print("="*60)

_sa = (
    _act_all[_act_all['sess_id'].notna() & (_act_all['sess_id'] != 'nan')]
    .sort_values(['person_id','timestamp'])
    .drop_duplicates(['person_id','sess_id'])
    [['person_id','timestamp']].copy()
)
_sa['prev_ts']  = _sa.groupby('person_id')['timestamp'].shift(1)
_sa['gap_days'] = (_sa['timestamp'] - _sa['prev_ts']).dt.total_seconds() / 86400.0
_sg  = _sa.dropna(subset=['gap_days'])
_sg  = _sg[_sg['gap_days'] > 0]
_uc  = _sg.groupby('person_id')['gap_days'].mean().reset_index(name='avg_gap')
_mg  = _uc['avg_gap'].median()
_mng = _uc['avg_gap'].mean()
print(f"Median avg inter-session gap : {_mg:.1f} days")
print(f"Mean avg inter-session gap   : {_mng:.1f} days")
print(f"Users with >1 session        : {len(_uc):,}")

fig_cad, ax_cad = _newfig(12, 6)
ax_cad.hist(_uc['avg_gap'].clip(upper=30), bins=30, color=_C5, edgecolor=_BG, linewidth=0.5, zorder=3)
ax_cad.axvline(_mg, color=_C6, linewidth=1.8, linestyle='--', label=f'Median: {_mg:.1f}d', zorder=5)
ax_cad.axvline(1,   color=_C3, linewidth=1.5, linestyle=':',  label='Daily  (1d)', zorder=5)
ax_cad.axvline(7,   color=_C4, linewidth=1.5, linestyle=':',  label='Weekly (7d)', zorder=5)
ax_cad.legend(facecolor='#2a2a2d', edgecolor='#3a3a3d', labelcolor=_TXT, fontsize=9)
_sty(ax_cad, title='§5  Session Cadence — Avg Days Between Sessions (Activated Users)',
     xlabel='Avg Days Between Sessions (capped at 30)', ylabel='Number of Users')
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §6  POWER USER IDENTIFICATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §6  POWER USER IDENTIFICATION")
print("="*60)

_audf = _umet[_umet['activated'] == 1].copy()
_p90  = _audf['total_events'].quantile(0.90)
_pwrs = _audf[_audf['total_events'] >= _p90]
_regs = _audf[_audf['total_events'] <  _p90]
print(f"P90 threshold (events)   : {_p90:.0f}")
print(f"Power users              : {len(_pwrs):,}  avg events={_pwrs['total_events'].mean():.0f}  avg depth={_pwrs['depth_score'].mean():.2f}")
print(f"Regular activated        : {len(_regs):,}  avg events={_regs['total_events'].mean():.0f}  avg depth={_regs['depth_score'].mean():.2f}")
print(f"Power user avg months    : {_pwrs['active_months'].mean():.2f}  regular: {_regs['active_months'].mean():.2f}")

_mkw = {
    'Total Events\n(avg)' : (_pwrs['total_events'].mean(),     _regs['total_events'].mean()),
    'Depth Score\n(avg)'  : (_pwrs['depth_score'].mean(),      _regs['depth_score'].mean()),
    'Active Months\n(avg)': (_pwrs['active_months'].mean(),    _regs['active_months'].mean()),
    'Days Active\n(avg)'  : (_pwrs['days_active_span'].mean(), _regs['days_active_span'].mean()),
}

fig_pw, axes_pw = plt.subplots(1, 4, figsize=(16, 6), facecolor=_BG)
for _ki, (_mk, (_pv, _rv)) in enumerate(_mkw.items()):
    _axi = axes_pw[_ki]
    _axi.set_facecolor(_BG)
    _axi.bar(['Power\nUsers','Regular\nActivated'], [_pv, _rv], color=[_C6, _C1], edgecolor='none', zorder=3)
    _axi.set_title(_mk, color=_TXT, fontsize=11, fontweight='bold')
    _axi.tick_params(colors=_STXT, labelsize=9)
    for _sp2 in _axi.spines.values():
        _sp2.set_edgecolor('#3a3a3d')
    _axi.grid(axis='y', color='#3a3a3d', linewidth=0.5, alpha=0.6, zorder=0)
    for _xi2, _xv in enumerate([_pv, _rv]):
        _axi.text(_xi2, _xv * 1.02, f'{_xv:.1f}', ha='center', va='bottom', color=_TXT, fontsize=9, fontweight='bold')

plt.suptitle('§6  Power Users (Top Decile) vs Regular Activated Users', color=_TXT,
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()

# ─────────────────────────────────────────────────────────────────────────────
# §7  EVENT SEQUENCING
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  §7  EVENT SEQUENCING — First 3 Events After Day 7")
print("="*60)

_seq = (
    _post7.sort_values(['person_id','timestamp'])
    .groupby('person_id').head(3).copy()
)
_seq['ev_rank'] = _seq.groupby('person_id').cumcount() + 1
_sqp = _seq.pivot(index='person_id', columns='ev_rank', values='event')
_sqp.columns = [f'e{int(c)}' for c in _sqp.columns]

_e1 = _sqp['e1'].value_counts().head(10) if 'e1' in _sqp.columns else pd.Series(dtype=int)
_e2 = _sqp['e2'].value_counts().head(10) if 'e2' in _sqp.columns else pd.Series(dtype=int)
_e3 = _sqp['e3'].value_counts().head(10) if 'e3' in _sqp.columns else pd.Series(dtype=int)

print("Top 10 first events (post day-7):")
print(_e1.to_string())
print("\nTop 10 second events:")
print(_e2.to_string())
print("\nTop 10 third events:")
print(_e3.to_string())

_sqp_full = _sqp.dropna()
if len(_sqp_full) > 0:
    _sqp_full = _sqp_full.copy()
    _sqp_full['sequence'] = (_sqp_full['e1'].str.replace('_',' ') + ' → ' +
                              _sqp_full['e2'].str.replace('_',' ') + ' → ' +
                              _sqp_full['e3'].str.replace('_',' '))
    _tseqs = _sqp_full['sequence'].value_counts().head(10)
    print("\nTop 10 full 3-event sequences:")
    print(_tseqs.to_string())

_tall = pd.concat([_e1.rename('p1'), _e2.rename('p2'), _e3.rename('p3')], axis=1).fillna(0)
_tall = _tall.loc[_e1.index]

fig_seq, ax_seq = _newfig(14, 8)
_sx = np.arange(len(_tall))
_ws = 0.28
ax_seq.bar(_sx - _ws, _tall['p1'], width=_ws, color=_C1, label='1st Event', edgecolor='none', zorder=3)
ax_seq.bar(_sx,        _tall['p2'], width=_ws, color=_C2, label='2nd Event', edgecolor='none', zorder=3)
ax_seq.bar(_sx + _ws,  _tall['p3'], width=_ws, color=_C3, label='3rd Event', edgecolor='none', zorder=3)
ax_seq.set_xticks(_sx)
ax_seq.set_xticklabels([e.replace('_',' ') for e in _tall.index],
                        rotation=35, ha='right', fontsize=9, color=_TXT)
ax_seq.legend(facecolor='#2a2a2d', edgecolor='#3a3a3d', labelcolor=_TXT, fontsize=9)
_sty(ax_seq, title='§7  Event Sequencing — Top 10 Events in First 3 Steps After Day-7 Mark',
     xlabel='Event Type', ylabel='User Count')
plt.tight_layout()

print("\n" + "="*60)
print("  ✓ All 7 post-activation analyses complete")
print("="*60)
