
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve, classification_report, confusion_matrix
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

# ─── Zerve Design System ──────────────────────────────────────────────────────
BG_CLR   = '#1D1D20'
TXT_CLR  = '#fbfbff'
STXT_CLR = '#909094'
CLR_LASSO = '#A1C9F4'
CLR_RIDGE = '#FFB482'
CLR_POS   = '#8DE5A1'
CLR_NEG   = '#FF9F9B'

# ─── 1. PREPROCESSING ─────────────────────────────────────────────────────────
_df = ml_dataset_7d.copy()
_y  = _df['activated_post7d'].values

_num_cols = ['depth_score_7d', 'total_events_7d'] + \
            [c for c in _df.columns if c.startswith('evt_')]

# Platform: low-cardinality one-hot (web, posthog-python)
_plat = _df['platform'].fillna('unknown').str.strip().str.lower()
for _pv in ['web', 'posthog-python']:
    _df['plat_' + _pv.replace('-', '_')] = (_plat == _pv).astype(int)
_plat_cols = ['plat_web', 'plat_posthog_python']

# OS: low-cardinality one-hot (top 4)
_os_raw = _df['os'].fillna('unknown').str.strip()
_os_map = {'Windows': 'os_windows', 'Linux': 'os_linux',
           'Mac OS X': 'os_mac_osx', 'Android': 'os_android'}
for _oval, _ocol in _os_map.items():
    _df[_ocol] = (_os_raw == _oval).astype(int)
_os_cols = list(_os_map.values())

# No country features — country_freq removed
_feature_cols_model = _num_cols + _plat_cols + _os_cols
_X = _df[_feature_cols_model].values.astype(float)

print("=" * 65)
print("  LASSO & RIDGE LOGISTIC REGRESSION — ACTIVATION PREDICTION")
print("=" * 65)
print(f"  Dataset  : {_X.shape[0]:,} users  |  {_X.shape[1]} features")
print(f"  Positive : {int(_y.sum()):,} ({_y.mean():.1%}) activated after 7d")
print(f"  Negative : {int((1-_y).sum()):,} ({(1-_y).mean():.1%}) not activated")
print(f"  Features : {len(_num_cols)} numeric  |  {len(_plat_cols)} platform OHE"
      f"  |  {len(_os_cols)} OS OHE  |  0 country (removed)")

# ─── 2. TRAIN / TEST SPLIT 80/20 STRATIFIED ───────────────────────────────────
_X_train, _X_test, _y_train, _y_test = train_test_split(
    _X, _y, test_size=0.2, random_state=42, stratify=_y
)
print(f"\n  Train: {len(_y_train):,}  |  Test: {len(_y_test):,}")
print(f"  Train activation: {_y_train.mean():.1%}  |  Test: {_y_test.mean():.1%}")

# ─── 3. SCALE + 5-FOLD CV TUNE C ──────────────────────────────────────────────
_scaler = StandardScaler()
_Xtr_sc = _scaler.fit_transform(_X_train)
_Xte_sc = _scaler.transform(_X_test)

_C_grid = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
_cv     = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

_lasso_cv, _ridge_cv = [], []
for _C in _C_grid:
    _lasso_cv.append(cross_val_score(
        LogisticRegression(penalty='l1', solver='liblinear', C=_C,
                           class_weight='balanced', max_iter=1000, random_state=42),
        _Xtr_sc, _y_train, cv=_cv, scoring='roc_auc').mean())
    _ridge_cv.append(cross_val_score(
        LogisticRegression(penalty='l2', solver='liblinear', C=_C,
                           class_weight='balanced', max_iter=1000, random_state=42),
        _Xtr_sc, _y_train, cv=_cv, scoring='roc_auc').mean())

_best_C_lasso_mod = _C_grid[int(np.argmax(_lasso_cv))]
_best_C_ridge_mod = _C_grid[int(np.argmax(_ridge_cv))]

print(f"\n  CV TUNING (5-fold, ROC-AUC):")
print(f"  {'C':>8}  {'Lasso':>10}  {'Ridge':>10}")
print(f"  {'─'*8}  {'─'*10}  {'─'*10}")
for _C, _la, _ri in zip(_C_grid, _lasso_cv, _ridge_cv):
    _lmark = ' ←' if _C == _best_C_lasso_mod else ''
    _rmark = ' ←' if _C == _best_C_ridge_mod else ''
    print(f"  {_C:>8.3f}  {_la:>10.4f}{_lmark}  {_ri:>10.4f}{_rmark}")
print(f"\n  Best C — Lasso: {_best_C_lasso_mod}  |  Ridge: {_best_C_ridge_mod}")

# ─── 4. FIT FINAL MODELS ──────────────────────────────────────────────────────
lasso_model_7d = LogisticRegression(penalty='l1', solver='liblinear',
                                     C=_best_C_lasso_mod, class_weight='balanced',
                                     max_iter=1000, random_state=42)
lasso_model_7d.fit(_Xtr_sc, _y_train)

ridge_model_7d = LogisticRegression(penalty='l2', solver='liblinear',
                                     C=_best_C_ridge_mod, class_weight='balanced',
                                     max_iter=1000, random_state=42)
ridge_model_7d.fit(_Xtr_sc, _y_train)

# ─── 5. EVALUATE ──────────────────────────────────────────────────────────────
_lasso_prob = lasso_model_7d.predict_proba(_Xte_sc)[:, 1]
_ridge_prob = ridge_model_7d.predict_proba(_Xte_sc)[:, 1]
_lasso_pred = lasso_model_7d.predict(_Xte_sc)
_ridge_pred = ridge_model_7d.predict(_Xte_sc)

lasso_auc_7d = roc_auc_score(_y_test, _lasso_prob)
ridge_auc_7d = roc_auc_score(_y_test, _ridge_prob)
_n_nonzero = int(np.sum(lasso_model_7d.coef_[0] != 0))

print(f"\n  {'='*55}")
print(f"  TEST SET RESULTS")
print(f"  {'='*55}")
print(f"  Lasso (L1) ROC-AUC : {lasso_auc_7d:.4f}  |  Non-zero: {_n_nonzero}/{len(_feature_cols_model)}")
print(f"  Ridge (L2) ROC-AUC : {ridge_auc_7d:.4f}  |  (all {len(_feature_cols_model)} retained)")

print(f"\n  CLASSIFICATION REPORT — Lasso (L1):")
print(classification_report(_y_test, _lasso_pred, target_names=['Not Activated', 'Activated']))
print(f"  CLASSIFICATION REPORT — Ridge (L2):")
print(classification_report(_y_test, _ridge_pred, target_names=['Not Activated', 'Activated']))

_cm_lasso = confusion_matrix(_y_test, _lasso_pred)
_cm_ridge = confusion_matrix(_y_test, _ridge_pred)
print(f"  Confusion Matrix — Lasso: TN={_cm_lasso[0,0]} FP={_cm_lasso[0,1]} "
      f"FN={_cm_lasso[1,0]} TP={_cm_lasso[1,1]}")
print(f"  Confusion Matrix — Ridge: TN={_cm_ridge[0,0]} FP={_cm_ridge[0,1]} "
      f"FN={_cm_ridge[1,0]} TP={_cm_ridge[1,1]}")

# ─── 6. ROC CURVES CHART ──────────────────────────────────────────────────────
_fpr_l, _tpr_l, _ = roc_curve(_y_test, _lasso_prob)
_fpr_r, _tpr_r, _ = roc_curve(_y_test, _ridge_prob)

fig_roc_curves_7d, ax_roc = plt.subplots(figsize=(9, 7))
fig_roc_curves_7d.patch.set_facecolor(BG_CLR)
ax_roc.set_facecolor(BG_CLR)
ax_roc.plot(_fpr_l, _tpr_l, color=CLR_LASSO, lw=2.5,
            label=f'Lasso L1  (AUC = {lasso_auc_7d:.3f})')
ax_roc.plot(_fpr_r, _tpr_r, color=CLR_RIDGE, lw=2.5,
            label=f'Ridge L2  (AUC = {ridge_auc_7d:.3f})')
ax_roc.plot([0, 1], [0, 1], color=STXT_CLR, lw=1.2, ls='--', label='Random baseline')
ax_roc.set_title('ROC Curves — Activation Prediction (7-Day Window)',
                 color=TXT_CLR, fontsize=14, fontweight='bold', pad=14)
ax_roc.set_xlabel('False Positive Rate', color=STXT_CLR, fontsize=11)
ax_roc.set_ylabel('True Positive Rate', color=STXT_CLR, fontsize=11)
ax_roc.tick_params(colors=TXT_CLR, labelsize=10)
ax_roc.legend(framealpha=0.15, labelcolor=TXT_CLR, fontsize=11,
              facecolor=BG_CLR, edgecolor=STXT_CLR, loc='lower right')
for _sp in ax_roc.spines.values():
    _sp.set_edgecolor(STXT_CLR)
ax_roc.set_xlim(0, 1)
ax_roc.set_ylim(0, 1)
plt.tight_layout()

# ─── 7. LASSO FEATURE IMPORTANCE CHART ────────────────────────────────────────
_coef_ser = lasso_model_7d.coef_[0]
_coef_df  = pd.DataFrame({'feature': _feature_cols_model, 'coef': _coef_ser})
_coef_df  = _coef_df[_coef_df['coef'] != 0].copy()
_coef_df['abs'] = _coef_df['coef'].abs()
_coef_df  = _coef_df.sort_values('abs', ascending=True).reset_index(drop=True)

def _fmt_label(name):
    n = (name
         .replace('evt_', '')
         .replace('plat_', 'platform: ')
         .replace('os_windows', 'OS: Windows')
         .replace('os_linux', 'OS: Linux')
         .replace('os_mac_osx', 'OS: Mac OSX')
         .replace('os_android', 'OS: Android')
         .replace('depth_score_7d', 'Depth Score (7d)')
         .replace('total_events_7d', 'Total Events (7d)')
         .replace('_', ' '))
    return n[:1].upper() + n[1:] if n and n[0].islower() else n

_coef_df['label'] = _coef_df['feature'].apply(_fmt_label)
_bar_colors = [CLR_POS if v > 0 else CLR_NEG for v in _coef_df['coef']]

fig_lasso_coefs_7d, ax_imp = plt.subplots(figsize=(10, max(5, len(_coef_df) * 0.45)))
fig_lasso_coefs_7d.patch.set_facecolor(BG_CLR)
ax_imp.set_facecolor(BG_CLR)

_bh = ax_imp.barh(_coef_df['label'].tolist(), _coef_df['coef'].tolist(),
                  color=_bar_colors, edgecolor='none', height=0.7)
for _b, _v in zip(_bh, _coef_df['coef']):
    _xoff = 0.004 if _v >= 0 else -0.004
    ax_imp.text(_v + _xoff, _b.get_y() + _b.get_height() / 2,
                f'{_v:+.3f}', va='center', ha='left' if _v >= 0 else 'right',
                color=TXT_CLR, fontsize=8.5)

ax_imp.axvline(0, color=STXT_CLR, lw=1.2, alpha=0.7)
ax_imp.set_title(f'Lasso L1 — Non-Zero Feature Coefficients  ({_n_nonzero} selected)',
                 color=TXT_CLR, fontsize=13, fontweight='bold', pad=12)
ax_imp.set_xlabel('Coefficient (log-odds contribution)', color=STXT_CLR, fontsize=10)
ax_imp.tick_params(colors=TXT_CLR, labelsize=9.5)
ax_imp.set_yticks(range(len(_coef_df)))
ax_imp.set_yticklabels(_coef_df['label'].tolist(), color=TXT_CLR)
_handles = [Patch(facecolor=CLR_POS, label='Positive (↑ activation prob)'),
            Patch(facecolor=CLR_NEG, label='Negative (↓ activation prob)')]
ax_imp.legend(handles=_handles, loc='lower right', framealpha=0.15,
              facecolor=BG_CLR, edgecolor=STXT_CLR, labelcolor=TXT_CLR, fontsize=9)
for _sp in ax_imp.spines.values():
    _sp.set_edgecolor(STXT_CLR)
plt.tight_layout()

# ─── 8. BEST MODEL SELECTION ──────────────────────────────────────────────────
best_model_name_7d = 'Lasso (L1)' if lasso_auc_7d >= ridge_auc_7d else 'Ridge (L2)'
best_auc_7d = max(lasso_auc_7d, ridge_auc_7d)

print(f"\n  {'='*55}")
print(f"  BEST MODEL: {best_model_name_7d}  (ROC-AUC = {best_auc_7d:.4f})")
print(f"  {'='*55}")
if best_model_name_7d == 'Lasso (L1)':
    print(f"  • Lasso AUC ({lasso_auc_7d:.4f}) ≥ Ridge ({ridge_auc_7d:.4f})")
    print(f"  • Selects {_n_nonzero}/{len(_feature_cols_model)} features — sparse & interpretable")
    print(f"  • Directly reveals the key behaviours driving activation")
else:
    print(f"  • Ridge AUC ({ridge_auc_7d:.4f}) > Lasso ({lasso_auc_7d:.4f})")
    print(f"  • More stable with correlated event features")
    print(f"  • Lasso retained {_n_nonzero}/{len(_feature_cols_model)} features")

print(f"\n  AUC > 0.60 target: {'✓ MET' if best_auc_7d > 0.60 else '✗ NOT MET'} ({best_auc_7d:.4f})")
print(f"  ✓ Both models fitted  ✓ ROC curves  ✓ Feature importance chart")
print(f"  ✓ No country features in model")
