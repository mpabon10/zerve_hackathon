
import pandas as pd
import numpy as np
import time
import io

CSV_FILE = "zerve_hackathon_for_reviewc8fa7c7.csv"

# ── Benchmark: raw load time ──────────────────────────────────────────────────
t0 = time.perf_counter()
profile_df = pd.read_csv(CSV_FILE)
load_time = time.perf_counter() - t0

# ── Shape ─────────────────────────────────────────────────────────────────────
n_rows, n_cols = profile_df.shape

# ── Memory footprint ──────────────────────────────────────────────────────────
mem_bytes   = profile_df.memory_usage(deep=True).sum()
mem_mb      = mem_bytes / 1_048_576

# ── Missing values ────────────────────────────────────────────────────────────
missing_counts  = profile_df.isnull().sum()
missing_pct     = (missing_counts / n_rows * 100).round(2)

# ── Cardinality ───────────────────────────────────────────────────────────────
cardinality = profile_df.nunique()

# ── dtypes ───────────────────────────────────────────────────────────────────
dtype_counts = profile_df.dtypes.value_counts()

# ══════════════════════════════════════════════════════════════════════════════
# REPORT
# ══════════════════════════════════════════════════════════════════════════════
SEP = "=" * 60

print(SEP)
print("  DATASET PROFILE REPORT")
print(SEP)
print(f"  File            : {CSV_FILE}")
print(f"  Rows            : {n_rows:,}")
print(f"  Columns         : {n_cols:,}")
print(f"  Load time       : {load_time:.3f}s")
print(f"  Memory (deep)   : {mem_mb:.2f} MB  ({mem_bytes:,} bytes)")
print()

# dtype breakdown
print(f"{'─'*60}")
print("  DTYPE BREAKDOWN")
print(f"{'─'*60}")
for dtype, cnt in dtype_counts.items():
    print(f"  {str(dtype):<15}: {cnt} column(s)")
print()

# Per-column detail
print(f"{'─'*60}")
print(f"  {'Column':<30} {'DType':<12} {'Missing':>8} {'Miss%':>7} {'Cardinality':>13}")
print(f"{'─'*60}")
for col in profile_df.columns:
    print(
        f"  {col:<30} "
        f"{str(profile_df[col].dtype):<12} "
        f"{missing_counts[col]:>8,} "
        f"{missing_pct[col]:>6.2f}% "
        f"{cardinality[col]:>13,}"
    )

print()
print(SEP)
print("  BASELINE BENCHMARK SUMMARY")
print(SEP)
print(f"  CSV size on disk  : {298_974_920 / 1_048_576:.1f} MB")
print(f"  Load time         : {load_time:.3f} s")
print(f"  In-memory size    : {mem_mb:.2f} MB")
print(f"  Compression ratio : {298_974_920 / mem_bytes:.2f}x  (disk / RAM)")
print(SEP)

# Columns with any missing data – quick highlight
cols_with_missing = missing_counts[missing_counts > 0]
if len(cols_with_missing):
    print(f"\n  ⚠  Columns with missing values ({len(cols_with_missing)}):")
    for col, cnt in cols_with_missing.items():
        print(f"     • {col}: {cnt:,} missing ({missing_pct[col]:.2f}%)")
else:
    print("\n  ✓  No missing values detected.")

print()
