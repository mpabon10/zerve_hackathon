
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# BUILD USER-LEVEL METRICS TABLE
# All 3 success metrics computed per person_id
# ─────────────────────────────────────────────────────────────────────────────

# Parse timestamps (string → datetime, UTC-aware)
_ts  = pd.to_datetime(opt_df['timestamp'],  utc=True, errors='coerce')
_cat = pd.to_datetime(opt_df['created_at'], utc=True, errors='coerce')
_lib = opt_df['prop_$lib'].astype(str)
_os  = opt_df['prop_$os'].astype(str)
_geo = opt_df['prop_$geoip_country_code'].astype(str)
_dev = opt_df['prop_$device_type'].astype(str)
_evt = opt_df['event'].astype(str)
_pid = opt_df['person_id'].astype(str)

_working = pd.DataFrame({
    'person_id' : _pid,
    'event'     : _evt,
    'timestamp' : _ts,
    'created_at': _cat,
    'lib'       : _lib,
    'os'        : _os,
    'country'   : _geo,
    'device'    : _dev,
    'credits'   : opt_df['prop_credits_used'] if 'prop_credits_used' in opt_df.columns else opt_df['prop_credit_amount'],
})

# ── METRIC 1: User Activation Rate ──────────────────────────────────────────
ACTIVATION_EVENTS = [
    'block_create', 'canvas_create', 'run_block',
    'agent_message', 'agent_block_run', 'agent_block_created'
]

# Signup date = min created_at per user
_signup  = _working.groupby('person_id')['created_at'].min().rename('signup_dt')
_first_act_ts = _working.groupby('person_id')['timestamp'].min().rename('first_event_ts')

# Activation: any signal event within 7 days of signup
_act_events = _working[_working['event'].isin(ACTIVATION_EVENTS)].copy()
_act_events = _act_events.merge(_signup.reset_index(), on='person_id')
_act_events['days_from_signup'] = (_act_events['timestamp'] - _act_events['signup_dt']).dt.total_seconds() / 86400
_act_events_7d = _act_events[_act_events['days_from_signup'] <= 7]
_activated_users = set(_act_events_7d['person_id'].unique())

# ── METRIC 2: Feature Adoption Depth Score ──────────────────────────────────
FEATURE_ZONES = ['agent', 'block', 'canvas', 'app', 'files', 'run', 'scheduled_job', 'source_control']

def _get_zone(evt_name):
    for zone in FEATURE_ZONES:
        if evt_name.startswith(zone):
            return zone
    return 'other'

_working['zone'] = _working['event'].map(_get_zone)
_depth = _working.groupby('person_id')['zone'].nunique().rename('depth_score')

def _depth_label(d):
    if d == 1:   return 'Explorer (1 zone)'
    elif d <= 3: return 'Builder (2–3 zones)'
    else:        return 'Power User (4+ zones)'

# ── METRIC 3: Activity Month Range for MAU Retention ────────────────────────
_working['ym'] = _working['timestamp'].dt.to_period('M')

# ── PER-USER SEGMENTATION ATTRIBUTES (mode of non-null values) ──────────────
def _safe_mode(s):
    v = s.dropna()
    v = v[v != 'nan']
    return v.mode().iloc[0] if len(v) > 0 else np.nan

_seg_cols = ['lib', 'os', 'country', 'device']
_segs = _working.groupby('person_id')[_seg_cols].agg(_safe_mode)

# ── ASSEMBLE USER-LEVEL TABLE ────────────────────────────────────────────────
_user_stats = _working.groupby('person_id').agg(
    total_events      = ('event',     'count'),
    distinct_events   = ('event',     'nunique'),
    first_seen        = ('timestamp', 'min'),
    last_seen         = ('timestamp', 'max'),
    total_credits     = ('credits',   'sum'),
    active_months     = ('ym',        'nunique'),
).reset_index()

_user_stats = _user_stats.merge(_signup.reset_index(),     on='person_id', how='left')
_user_stats = _user_stats.merge(_first_act_ts.reset_index(), on='person_id', how='left')
_user_stats = _user_stats.merge(_depth.reset_index(),      on='person_id', how='left')
_user_stats = _user_stats.merge(_segs.reset_index(),       on='person_id', how='left')

_user_stats['activated']         = _user_stats['person_id'].isin(_activated_users).astype(int)
_user_stats['depth_segment']     = _user_stats['depth_score'].map(_depth_label)
_user_stats['days_active_span']  = (_user_stats['last_seen'] - _user_stats['first_seen']).dt.days

# Lifecycle stage: based on last_seen relative to max(last_seen) in the dataset
_ref_date = _user_stats['last_seen'].max()
_user_stats['days_since_last']   = (_ref_date - _user_stats['last_seen']).dt.days
_user_stats['lifecycle_stage']   = pd.cut(
    _user_stats['days_since_last'],
    bins=[-1, 7, 30, 60, 9999],
    labels=['New', 'Active', 'At-Risk', 'Churned']
)

# Signup cohort month
_user_stats['signup_cohort'] = _user_stats['signup_dt'].dt.to_period('M').astype(str)

user_metrics_df = _user_stats.copy()

# ── SUMMARY PRINT ────────────────────────────────────────────────────────────
_n_users      = len(user_metrics_df)
_n_activated  = user_metrics_df['activated'].sum()
_act_rate     = _n_activated / _n_users * 100
_median_depth = user_metrics_df['depth_score'].median()

print("=" * 60)
print("  USER METRICS — SUMMARY")
print("=" * 60)
print(f"  Total users (person_id)  : {_n_users:,}")
print(f"  Activated users (7d)     : {_n_activated:,}  ({_act_rate:.1f}%)")
print(f"  Median depth score       : {_median_depth:.1f} zones")
print()
print("  Depth Segment Distribution:")
print(user_metrics_df['depth_segment'].value_counts().to_string())
print()
print("  Lifecycle Stage Distribution:")
print(user_metrics_df['lifecycle_stage'].value_counts().to_string())
print()
print("  Signup Cohorts:")
print(user_metrics_df['signup_cohort'].value_counts().sort_index().to_string())
print("=" * 60)
