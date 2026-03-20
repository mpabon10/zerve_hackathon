
import pandas as pd
import numpy as np
import time

CSV_FILE = "zerve_hackathon_for_reviewc8fa7c7.csv"

# ─────────────────────────────────────────────────────────────
# BASELINE metrics (from profiling block)
# ─────────────────────────────────────────────────────────────
baseline_load_time = load_time        # seconds
baseline_mem_mb    = mem_mb           # MB
baseline_n_cols    = n_cols           # 107

# ─────────────────────────────────────────────────────────────
# STRATEGY derived from profiling results
# ─────────────────────────────────────────────────────────────
# cardinality / missing_pct are Series with positional integer index from
# the profiler block; re-index them on column names for safe lookup.
_col_names = profile_df.columns.tolist()
card_by_col    = pd.Series(cardinality.values,    index=_col_names)
miss_pct_by_col = pd.Series(missing_pct.values,  index=_col_names)

HIGH_NULL_THRESHOLD = 80.0   # %

# 1. Drop columns with >90 % missing
cols_to_drop_null = list(miss_pct_by_col[miss_pct_by_col > HIGH_NULL_THRESHOLD].index)

# 2. Drop the anonymous row-index column
redundant_cols = ["Unnamed: 0"]
cols_to_drop = list(set(cols_to_drop_null + redundant_cols))

# 3. Date columns to parse at load time
date_cols = [
    "created_at", "timestamp", "_inserted_at",
    "prop_$sent_at", "prop_$initialization_time", "prop_$last_posthog_reset",
]
active_date_cols = [c for c in date_cols if c not in cols_to_drop]

# 4. Low-cardinality columns → categorical (cardinality ≤ 200, not being dropped)
LOW_CARD_THRESH = 200
cat_candidates = [
    c for c in _col_names
    if (c not in cols_to_drop
        and c not in date_cols
        and card_by_col[c] <= LOW_CARD_THRESH)
]

# ─────────────────────────────────────────────────────────────
# OPTIMISED LOAD
# ─────────────────────────────────────────────────────────────
dtype_map = {c: "category" for c in cat_candidates}

_t_opt_start = time.perf_counter()

opt_df = pd.read_csv(
    CSV_FILE,
    dtype=dtype_map,
    parse_dates=active_date_cols,
    usecols=lambda c: c not in cols_to_drop,   # skip at read time
)

opt_load_time = time.perf_counter() - _t_opt_start

# ─────────────────────────────────────────────────────────────
# POST-LOAD OPTIMISATIONS
# ─────────────────────────────────────────────────────────────

# 5. Downcast remaining int64 columns
for _c in opt_df.select_dtypes(include=["int64"]).columns:
    opt_df[_c] = pd.to_numeric(opt_df[_c], downcast="signed")

# 6. Downcast float64 → float32
for _c in opt_df.select_dtypes(include=["float64"]).columns:
    opt_df[_c] = opt_df[_c].astype("float32")

# Flag high-null columns that were retained (50–90 % missing)
_remaining_miss = opt_df.isnull().sum() / len(opt_df) * 100
flagged_high_null = _remaining_miss[_remaining_miss > 50].sort_values(ascending=False)

# ─────────────────────────────────────────────────────────────
# BENCHMARK
# ─────────────────────────────────────────────────────────────
opt_mem_bytes     = opt_df.memory_usage(deep=True).sum()
opt_mem_mb        = opt_mem_bytes / 1_048_576
opt_n_cols        = opt_df.shape[1]
opt_n_rows        = opt_df.shape[0]

load_speedup      = baseline_load_time / opt_load_time
mem_reduction_mb  = baseline_mem_mb - opt_mem_mb
mem_reduction_pct = (mem_reduction_mb / baseline_mem_mb) * 100
cols_removed      = baseline_n_cols - opt_n_cols

# dtype summary (collapse duplicates)
_opt_dtype_summary = opt_df.dtypes.value_counts()

# ─────────────────────────────────────────────────────────────
# BEFORE / AFTER COMPARISON TABLE
# ─────────────────────────────────────────────────────────────
SEP2 = "=" * 66

print(SEP2)
print("  PIPELINE OPTIMISATION  ─  BEFORE vs AFTER")
print(SEP2)
print(f"  {'Metric':<38} {'Baseline':>11}  {'Optimised':>11}")
print(f"  {'─'*38} {'─'*11}  {'─'*11}")
print(f"  {'Load time (s)':<38} {baseline_load_time:>11.3f}  {opt_load_time:>11.3f}")
print(f"  {'Memory usage (MB)':<38} {baseline_mem_mb:>11.2f}  {opt_mem_mb:>11.2f}")
print(f"  {'Columns':<38} {baseline_n_cols:>11}  {opt_n_cols:>11}")
print(f"  {'Rows':<38} {n_rows:>11,}  {opt_n_rows:>11,}")
print(SEP2)
print(f"  {'Load speedup':<38} {'':>11}  {load_speedup:>10.2f}x")
print(f"  {'Memory saved (MB)':<38} {'':>11}  {mem_reduction_mb:>10.1f}")
print(f"  {'Memory reduction':<38} {'':>11}  {mem_reduction_pct:>9.1f}%")
print(f"  {'Columns removed':<38} {'':>11}  {cols_removed:>11}")
print(SEP2)

# Dtype breakdown (collapsed)
print("\n  DTYPE BREAKDOWN (optimised)")
print(f"  {'─'*40}")
for _dtype, _cnt in _opt_dtype_summary.items():
    print(f"  {str(_dtype):<24}: {_cnt} column(s)")

# Columns dropped
print(f"\n  DROPPED COLUMNS ({len(cols_to_drop)})")
print(f"  {'─'*60}")
for _c in sorted(cols_to_drop, key=str):
    _reason = "high null (>90%)" if _c in cols_to_drop_null else "redundant index"
    print(f"  • {str(_c):<48}  [{_reason}]")

# Categorical columns
print(f"\n  CATEGORICAL ENCODING APPLIED ({len(cat_candidates)} columns)")
print(f"  {'─'*60}")
for _c in sorted(cat_candidates, key=str):
    print(f"  • {str(_c):<48}  [cardinality={card_by_col[_c]}]")

# Flagged high-null columns (retained but flagged)
if len(flagged_high_null):
    print(f"\n  ⚠  HIGH-NULL COLUMNS RETAINED & FLAGGED ({len(flagged_high_null)})")
    print(f"  {'─'*60}")
    for _c, _pct in flagged_high_null.items():
        print(f"  • {str(_c):<48}  [{_pct:.1f}% missing]")

print(f"\n  ✓ Optimised DataFrame shape: {opt_df.shape}")
print(SEP2)
