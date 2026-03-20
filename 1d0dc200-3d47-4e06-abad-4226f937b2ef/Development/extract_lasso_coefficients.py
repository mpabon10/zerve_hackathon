
import pandas as pd
import numpy as np

# Reconstruct feature list (mirrors lasso_ridge_activation_model — no country)
_num_cols = ['depth_score_7d', 'total_events_7d'] + \
            [c for c in ml_dataset_7d.columns if c.startswith('evt_')]
_plat_cols = ['plat_web', 'plat_posthog_python']
_os_cols   = ['os_windows', 'os_linux', 'os_mac_osx', 'os_android']
_feature_cols_model = _num_cols + _plat_cols + _os_cols  # 23 features, no country

_n_feats = len(_feature_cols_model)
_coef_vals = lasso_model_7d.coef_[0]
_coef_df = pd.DataFrame({'feature': _feature_cols_model, 'coef': _coef_vals})
_coef_df['nonzero'] = _coef_df['coef'] != 0
_coef_df['abs']     = _coef_df['coef'].abs()
_coef_df_sorted     = _coef_df.sort_values('abs', ascending=False)

# All features (including zero)
print("=" * 65)
print(f"  LASSO COEFFICIENT TABLE — FULL FEATURE SET ({_n_feats} features, no country)")
print("=" * 65)
print(f"{'Feature':<50} {'Coef':>10}  {'Selected'}")
print("-" * 65)
for _, row in _coef_df_sorted.iterrows():
    sel = "✓ YES" if row['nonzero'] else "✗ zeroed"
    print(f"{row['feature']:<50} {row['coef']:>+10.4f}  {sel}")

print()
print("=" * 65)
print("  NON-ZERO FEATURES ONLY (Lasso selected)")
print("=" * 65)
_selected = _coef_df[_coef_df['nonzero']].sort_values('abs', ascending=False)
for _, row in _selected.iterrows():
    _odds_mult = np.exp(row['coef'])
    print(f"  {row['feature']:<50} coef={row['coef']:+.4f}  odds_mult={_odds_mult:.3f}x")

print()
print("=" * 65)
print("  ZEROED-OUT FEATURES (Lasso eliminated)")
print("=" * 65)
_zeroed = _coef_df[~_coef_df['nonzero']]
for _, row in _zeroed.iterrows():
    print(f"  {row['feature']}")

print()
print(f"  ✓ No country features in feature set")
print(f"  ✓ {len(_selected)}/{_n_feats} features selected by Lasso")
