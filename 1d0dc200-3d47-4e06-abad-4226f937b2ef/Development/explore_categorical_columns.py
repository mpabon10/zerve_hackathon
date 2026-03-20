# Print distinct categories for all categorical columns in opt_df
_cat_cols = [col for col, dtype in opt_df.dtypes.items() if str(dtype) == 'category']

print(f"Found {len(_cat_cols)} categorical columns in opt_df\n")
print("=" * 70)

for _col in _cat_cols:
    _cats = opt_df[_col].cat.categories.tolist()
    _n_cats = len(_cats)
    _null_count = opt_df[_col].isna().sum()
    
    print(f"\n📂 {_col}")
    print(f"   Cardinality: {_n_cats} | Nulls: {_null_count:,}")
    print(f"   Categories:")
    
    # Format categories readably — truncate long strings
    for _cat in _cats:
        _cat_str = str(_cat)
        _display = _cat_str if len(_cat_str) <= 80 else _cat_str[:77] + "..."
        print(f"     • {_display}")
    
    print("-" * 70)