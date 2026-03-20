
import pandas as pd
import numpy as np

SEP = "=" * 70
SEP2 = "-" * 70

# ─────────────────────────────────────────────────────────────────────────────
# 1. OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
print(SEP)
print("  DATASET DEEP DIVE  —  zerve_hackathon_for_review.csv")
print(SEP)
print(f"  Shape          : {opt_df.shape[0]:,} rows  ×  {opt_df.shape[1]} columns")
print(f"  Memory (opt)   : {opt_df.memory_usage(deep=True).sum() / 1_048_576:.1f} MB")
print()

# ─────────────────────────────────────────────────────────────────────────────
# 2. COLUMN NAMES & DTYPES
# ─────────────────────────────────────────────────────────────────────────────
print(SEP)
print("  COLUMN INVENTORY  (name | dtype | nulls% | cardinality)")
print(SEP)
_null_pct   = opt_df.isnull().mean() * 100
_cardinality = opt_df.nunique()
for _col in opt_df.columns:
    _dtype_str = str(opt_df[_col].dtype)
    _np = _null_pct[_col]
    _card = _cardinality[_col]
    print(f"  {_col:<62}  {_dtype_str:<22}  null={_np:5.1f}%  card={_card:,}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. DTYPE SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  DTYPE SUMMARY")
print(SEP)
_dtype_summary = opt_df.dtypes.astype(str).value_counts()
for _dtype, _cnt in _dtype_summary.items():
    print(f"  {_dtype:<28}  {_cnt:>3} column(s)")

# ─────────────────────────────────────────────────────────────────────────────
# 4. SAMPLE ROWS
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  SAMPLE ROWS (first 5)")
print(SEP)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 120)
pd.set_option("display.max_colwidth", 40)
print(opt_df.head(5).to_string(index=True))

# ─────────────────────────────────────────────────────────────────────────────
# 5. EVENT TYPES
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print(f"  EVENT TYPES  (unique: {opt_df['event'].nunique()})")
print(SEP)
_event_counts = opt_df["event"].value_counts()
print(f"  {'Event':<60}  {'Count':>8}  {'%':>6}")
print(f"  {'-'*60}  {'--------':>8}  {'------':>6}")
for _evt, _cnt in _event_counts.items():
    _pct = _cnt / len(opt_df) * 100
    print(f"  {str(_evt):<60}  {_cnt:>8,}  {_pct:>5.2f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 6. USER FIELDS
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  USER / IDENTITY FIELDS")
print(SEP)
_user_cols = [c for c in opt_df.columns if any(k in c.lower() for k in ["user", "person", "distinct", "userid"])]
for _uc in _user_cols:
    _n_unique = opt_df[_uc].nunique()
    _n_null   = opt_df[_uc].isna().sum()
    print(f"  {_uc:<52}  unique={_n_unique:>8,}  nulls={_n_null:>8,}")

# distinct_id vs person_id overlap
_n_distinct = opt_df["distinct_id"].nunique()
_n_person   = opt_df["person_id"].nunique()
print()
print(f"  distinct_id unique  : {_n_distinct:,}")
print(f"  person_id   unique  : {_n_person:,}")
print(f"  Rows per user (avg) : {len(opt_df) / max(_n_distinct, 1):.1f}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. DATE RANGES
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  DATE RANGES")
print(SEP)
# Try parsing string date columns safely
_date_col_candidates = ["timestamp", "created_at", "_inserted_at", "prop_$sent_at",
                         "prop_$initialization_time", "prop_$last_posthog_reset"]
for _dc in _date_col_candidates:
    if _dc not in opt_df.columns:
        print(f"  {_dc:<40}  [not in dataset]")
        continue
    _series = opt_df[_dc]
    if str(_series.dtype).startswith("datetime"):
        _min = _series.min()
        _max = _series.max()
        _n_null = _series.isna().sum()
        print(f"  {_dc:<40}  {str(_min)[:19]}  →  {str(_max)[:19]}  (nulls={_n_null:,})")
    else:
        # Parse on the fly for string columns (sample 10k for speed)
        _sample = _series.dropna().head(10_000)
        _parsed = pd.to_datetime(_sample, errors="coerce", utc=True)
        _n_valid = _parsed.notna().sum()
        if _n_valid > 0:
            print(f"  {_dc:<40}  {str(_parsed.min())[:19]}  →  {str(_parsed.max())[:19]}  (string col, sample-based)")
        else:
            print(f"  {_dc:<40}  [could not parse as datetime]")

# ─────────────────────────────────────────────────────────────────────────────
# 8. NUMERIC COLUMN DISTRIBUTIONS
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  NUMERIC COLUMN DISTRIBUTIONS")
print(SEP)
_num_cols = opt_df.select_dtypes(include=["float32", "float64", "int8", "int16", "int32", "int64"]).columns.tolist()
if _num_cols:
    _desc = opt_df[_num_cols].describe(percentiles=[0.25, 0.5, 0.75, 0.95]).T
    _desc["null%"] = (opt_df[_num_cols].isnull().mean() * 100).values
    print(_desc[["count", "mean", "std", "min", "25%", "50%", "75%", "95%", "max", "null%"]].to_string())
else:
    print("  No pure numeric columns found.")

# ─────────────────────────────────────────────────────────────────────────────
# 9. KEY CATEGORICAL DISTRIBUTIONS
# ─────────────────────────────────────────────────────────────────────────────
_key_cats = [
    "prop_$device_type", "prop_$browser", "prop_$os",
    "prop_$geoip_country_code", "prop_$lib", "prop_surface",
    "prop_tool_name", "prop_$python_runtime", "prop_$python_version",
]
print()
print(SEP)
print("  KEY CATEGORICAL DISTRIBUTIONS")
print(SEP)
for _kc in _key_cats:
    if _kc not in opt_df.columns:
        continue
    _vc = opt_df[_kc].value_counts(dropna=False).head(10)
    print(f"\n  ▸ {_kc}  (top 10 of {opt_df[_kc].nunique()} unique)")
    for _val, _cnt in _vc.items():
        _pct = _cnt / len(opt_df) * 100
        print(f"    {'<NaN>' if pd.isna(_val) else str(_val):<50}  {_cnt:>8,}  {_pct:>5.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 10. MISSING VALUE SUMMARY (top 20 worst columns)
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  TOP-20 COLUMNS BY MISSING %")
print(SEP)
_miss = (opt_df.isnull().mean() * 100).sort_values(ascending=False).head(20)
for _c, _pct in _miss.items():
    bar = "█" * int(_pct / 5)
    print(f"  {_c:<58}  {_pct:5.1f}%  {bar}")

# ─────────────────────────────────────────────────────────────────────────────
# 11. SUMMARY METADATA
# ─────────────────────────────────────────────────────────────────────────────
print()
print(SEP)
print("  METADATA SUMMARY")
print(SEP)
print(f"  Total rows              : {len(opt_df):,}")
print(f"  Total columns           : {len(opt_df.columns)}")
print(f"  Unique events           : {opt_df['event'].nunique()}")
print(f"  Unique distinct_ids     : {opt_df['distinct_id'].nunique():,}")
print(f"  Unique person_ids       : {opt_df['person_id'].nunique():,}")
_str_cols  = (opt_df.dtypes == object).sum() + (opt_df.dtypes.astype(str) == 'str').sum()
_cat_cols_n  = (opt_df.dtypes.astype(str) == 'category').sum()
_float_cols  = opt_df.select_dtypes(include=['float32','float64']).shape[1]
_dt_cols     = sum(1 for d in opt_df.dtypes if str(d).startswith('datetime'))
print(f"  String columns          : {_str_cols}")
print(f"  Category columns        : {_cat_cols_n}")
print(f"  Float columns           : {_float_cols}")
print(f"  Datetime columns        : {_dt_cols}")
print(f"  Fully null columns      : {int((opt_df.isnull().mean() == 1.0).sum())}")
print(f"  Columns with 0 nulls    : {int((opt_df.isnull().mean() == 0.0).sum())}")
print(SEP)
print("  ✓ Dataset exploration complete.")
print(SEP)
