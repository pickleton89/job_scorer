Below is a practical “upgrade recipe” that converts your current **job-skill-matrix-scoring.py** (3-2-1 method) into the richer **Classification × Emphasis × 0-5** framework you said you prefer.
Each step tells you **what to change**, **why**, and shows a ready-to-paste code fragment that slots into your existing file.

---

## 0  Files we’re modifying

Your present script already does nice CSV I/O, core-gap detection, and bonus-row capping . We’ll keep that skeleton and swap out the math.

---

## 1  Add the new lookup tables

```python
# --- NEW look-ups ---------------------------------------------------------
CLASS_WT = {
    "Essential": 3.0,
    "Important": 2.0,
    "Desirable": 1.0,
    "Implicit": 0.5,
}
MAX_ROW_SCORE = 3.0 * 1.5 * 5     # 22.5 (Essential × Critical × SelfScore=5)
```

Place these near the top, after your current imports.

---

## 2  Auto-detect the emphasis modifier

Replace your old free-text parsing with this helper (drop it under your “Scoring logic” section):

```python
CRITICAL = {"expert", "extensive", "demonstrated", "proven", "advanced"}
MINIMAL  = {"familiarity", "exposure", "limited"}

def emphasis_modifier(text: str) -> float:
    """Return +0.5 (Critical), 0.0 (Standard), or -0.5 (Minimal)."""
    t = text.lower()
    if any(w in t for w in CRITICAL):
        return +0.5
    if any(w in t for w in MINIMAL):
        return -0.5
    return 0.0
```

---

## 3  Extend `load_matrix()` to build the new numeric columns

Inside your existing `load_matrix` (after you coerce numeric columns), append:

```python
# Expect a column called 'Classification' and the JD bullet in 'Requirement'
if not {"Classification", "Requirement"}.issubset(df.columns):
    raise ValueError("CSV must contain 'Classification' and 'Requirement' columns.")

df["ClassWt"] = df["Classification"].map(CLASS_WT).fillna(0)
df["EmphMod"] = df["Requirement"].apply(emphasis_modifier)
```

(This preserves your original `Weight` column so older CSVs still load.)

---

## 4  Replace the old row-score math

Delete (or ignore) the block in `compute_scores` that creates `df["WeightedScore"]`  and insert:

```python
# New raw score
df["RowScoreRaw"] = df["ClassWt"] * (1 + df["EmphMod"]) * df["SelfScore"]

# Optional-row cap (keep your existing apply_bonus_cap *or* do simple scaling)
core_mask   = df["Classification"].isin(["Essential", "Important"])
bonus_mask  = ~core_mask
core_pts    = df.loc[core_mask,  "RowScoreRaw"].sum()
bonus_pts   = df.loc[bonus_mask, "RowScoreRaw"].sum()
allowed     = core_pts * 0.25         # 25 % cap
if bonus_pts > allowed and bonus_pts > 0:
    scale = allowed / bonus_pts
    df.loc[bonus_mask, "RowScoreRaw"] *= scale

# Normalise so every row ∈ [0,1]
df["RowScore"] = df["RowScoreRaw"] / MAX_ROW_SCORE
```

Rename your points variables:

```python
actual_points = df["RowScore"].sum()               # between 0 and row-count
max_points    = len(df)                            # each row could be 1.0
pct_fit       = actual_points / max_points if max_points else 0.0
```

Now %-fit is simply the **average normalised row score × 100**—no monster rows.

---

## 5  Upgrade the core-gap flag

Keep your existing check but switch from `Weight == 3` to *Classification == Essential*:

```python
core_gap_mask = (df["Classification"] == "Essential") & (df["SelfScore"] <= 1)
```

Your summary printing logic can stay unchanged.

---

## 6  Drop bonus-cap parameters you no longer need (optional)

If the 25 % cap is now hard-coded, you can remove the `--cap` CLI flag and the whole `apply_bonus_cap` branch – or leave it if you still want row-limit mode.

---

## 7  Re-test

```bash
python job-skill-matrix-scoring.py new_skillsheet.csv
```

You should see:

```
Fit % : 74.1   Verdict : Good match (minor gaps)
```

and a **core-gap override** if any Essential row is ≤ 1.

---

## 8  CSV header checklist for the new method

| Column         | Example value                                | Required? |
| -------------- | -------------------------------------------- | --------- |
| Requirement    | “Python scripting”                           | ✔         |
| Classification | Essential / Important / Desirable / Implicit | ✔         |
| SelfScore      | 0-5 integer                                  | ✔         |
| (others)       | Position, Notes, etc.                        | optional  |

If you still get data from the older 3-2-1 scorecard, keep the `Weight` column too; the script now ignores it but won’t crash.

---

### Result

You now have:

* **Granular 0–5 self-scores**
* **Keyword-driven emphasis (+0.5 / –0.5)**
* **Optional-skill cap + row normalisation** (so no single row hijacks the total)
* **Core-gap override** that short-circuits %-fit when a must-have is weak.

Drop these snippets into your current file and you’re ready to analyse any biotech JD with the richer framework. If you hit an edge case (e.g. unusual column names), let me know and we can tweak the loader.
