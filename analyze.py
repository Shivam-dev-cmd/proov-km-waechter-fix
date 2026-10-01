# analyze.py
# FINDINGS: The two strongest predictors of breakdown are km_since_service (cars that broke down
# averaged ~12,700 km into their service window vs ~7,700 for those that did not) and load_factor
# (0.66 vs 0.46). avg_daily_km also separates the groups clearly (176 vs 124). Total odometer_km
# and age_years show almost no difference between groups — the obvious assumption is wrong.
# Risk score = weighted sum of those three normalised columns (weights reflect group separation).

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# ── Step 1: compare group means to find separating columns ──────────────────
features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
print("=== Group means: broke_down=1 vs broke_down=0 ===")
print(df.groupby("broke_down")[features].mean().round(1).to_string())
print()

# ── Step 2: build a 0-100 risk score from the three columns that separate ───
# Normalise each column to [0, 1] across the whole fleet, then weight by
# how strongly the means differed between the two groups.
#   km_since_service : broke=12720 vs ok=7740  → diff ~4980  weight 0.45
#   load_factor      : broke=0.66  vs ok=0.46  → diff ~0.20  weight 0.35
#   avg_daily_km     : broke=176   vs ok=124   → diff ~52    weight 0.20

def normalise(series):
    lo, hi = series.min(), series.max()
    if hi == lo:
        return series * 0.0
    return (series - lo) / (hi - lo)

df["norm_km_since"]  = normalise(df["km_since_service"])
df["norm_load"]      = normalise(df["load_factor"])
df["norm_daily_km"]  = normalise(df["avg_daily_km"])

df["risk_score"] = (
    df["norm_km_since"] * 0.45 +
    df["norm_load"]     * 0.35 +
    df["norm_daily_km"] * 0.20
) * 100

# ── Step 3: print ranked list ────────────────────────────────────────────────
ranked = df[["car_id", "km_since_service", "load_factor", "avg_daily_km", "risk_score", "broke_down"]] \
           .sort_values("risk_score", ascending=False) \
           .reset_index(drop=True)

ranked.index += 1   # rank starts at 1
print("=== Fleet ranked by breakdown risk (highest first) ===")
print(ranked.to_string())
print()
print("Cars flagged by the 80% rule (km_since_service >= 12000) vs top-20 by risk:")
flag_ids  = set(df.loc[df["km_since_service"] >= 12000, "car_id"])
risk_ids  = set(ranked.head(20)["car_id"])
early_warning = risk_ids - flag_ids
print("  Extra cars risk model catches early (not yet 80%%):", sorted(early_warning))
