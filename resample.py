import pandas as pd
import numpy as np

# ---- config ----
infile  = "apple_watch_hr.csv"      # columns: timestamp,value   (tz ok)
outfile = "data_5s.csv"
target_freq = "5s"        # 5-second grid
noise_pct = 0.02          # 2% of series std as noise scale

# ---- load & clean ----
df = pd.read_csv(infile)

# pick columns if your csv still has extra timestamp fields
# (keeps the LAST timestamp-looking col + last numeric-looking col)
if "timestamp" not in df.columns:
    # try to auto-detect timestamp column
    ts_cols = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()]
    if ts_cols:
        ts_col = ts_cols[-1]
    else:
        ts_col = df.columns[0]  # fallback
else:
    ts_col = "timestamp"

val_candidates = [c for c in df.columns if c != ts_col]
val_col = "value" if "value" in df.columns else val_candidates[-1]

# parse datetime (keeps timezone if present)
df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce", utc=False)

# numeric-ify values
df[val_col] = pd.to_numeric(df[val_col], errors="coerce")

# drop junk, set index, sort
df = df.dropna(subset=[ts_col, val_col]).set_index(ts_col).sort_index()

# ---- upsample & interpolate ----
# create regular 5s grid across the observed span
idx = pd.date_range(start=df.index.min(), end=df.index.max(), freq=target_freq)
df = df.drop_duplicates()
df_5s = df.reindex(idx)  # upsample -> NaNs between known points

# time-aware interpolation along datetime index
df_5s[val_col] = df_5s[val_col].interpolate(
    method="time",
    limit_direction="both"   # fill leading/trailing edges too
)

# ---- add noise (optional) ----
sigma = noise_pct * df_5s[val_col].std(skipna=True)
if np.isfinite(sigma) and sigma > 0:
    df_5s[val_col] = df_5s[val_col] + np.random.normal(0, sigma, size=len(df_5s))

# ---- tidy & save ----
out = df_5s.reset_index().rename(columns={"index": "timestamp", val_col: "value"})
out.to_csv(outfile, index=False)

print(out.head(12))
print(f"\nWrote {len(out)} rows → {outfile}")
