Here is a prioritized list of changes to update the Python script. Please implement them in the order presented:

1.  **Remove Old Scoring Logic from `compute_scores` Function**
    *   **Why:** To make the function exclusively support the new scoring system (Classification-based with emphasis modifiers) and remove obsolete code.
    *   **How:**
        *   In the `compute_scores` function, locate the line `if new_format:`.
        *   Delete the entire `else:` block associated with this `if` statement (the block that starts with `# Original scoring logic (for backward compatibility)`).
        *   Remove the `new_format` variable declaration and the `if new_format:` check itself. The code that was inside the `if new_format:` block will now be the only logic in the function.
        *   Remove the `effective_total_weight: int` parameter from the function definition, as it's no longer used by the new system's `max_points` calculation.

2.  **Remove Old CSV Format Handling from `load_matrix` Function**
    *   **Why:** To ensure the script only loads and processes CSVs in the new format (expecting "Classification" and "Requirement" columns).
    *   **How:**
        *   In the `load_matrix` function, locate the `if "Classification" in df.columns:` line.
        *   Delete the entire `else:` block associated with this `if` statement (the block that starts with `# Original format - keep existing behavior`).
        *   The `if not {"Classification", "Requirement"}.issubset(df.columns):` check within the first part of the `if` block should now be the primary validation. If these columns are missing, it should raise the `ValueError`.
        *   The line `df["Weight"] = df["Classification"].map(CLASS_WT).fillna(0)` (which creates a "Weight" column for backward compatibility with `apply_bonus_cap`) can now be **removed**, as `apply_bonus_cap` will be removed in the next step, and the new scoring system primarily uses `ClassWt`.

3.  **Remove the `apply_bonus_cap` Function Entirely**
    *   **Why:** This function is tied to the old bonus system (Weight-1 rows, row limits, percentage caps on those specific rows) and the `--cap` CLI argument. The new scoring system in `compute_scores` implements its own, different bonus capping mechanism (proportional scaling of "Desirable" and "Implicit" items based on 25% of core `ClassWt` points).
    *   **How:**
        *   Delete the entire function definition for `apply_bonus_cap(df_in: pd.DataFrame, ...)`.
        *   In the `main()` function, delete the line: `df_eff, eff_weight = apply_bonus_cap(df_raw, cap_pct, cap_rows)`.
        *   Modify the subsequent line to pass `df_raw` directly to `compute_scores`. It should become: `metrics = compute_scores(df_raw)` (since `effective_total_weight` was removed from `compute_scores`'s parameters in step 1).

4.  **Remove the `--cap` Command-Line Argument**
    *   **Why:** This argument controlled the behavior of the `apply_bonus_cap` function, which is being removed.
    *   **How:**
        *   In the `main()` function, within the `argparse` setup, delete the following lines:
            ```python
            parser.add_argument(
                "--cap",
                type=float,
                default=0.25,
                help="Bonus cap: ≤1 → percent mode; >1 → row-limit mode (int)",
            )
            ```
        *   Also, delete the lines that parse this argument:
            ```python
            cap_rows = int(args.cap) if args.cap > 1 else None
            cap_pct = None if args.cap > 1 else args.cap
            ```

5.  **Standardize and Clarify Bonus Capping within `compute_scores`**
    *   **Why:** To make the new system's bonus capping logic (25% of core points, applied proportionally) clear and use constants.
    *   **How:**
        *   Inside `compute_scores`, locate the bonus capping section for the new format (around `max_bonus_points = core_weight * 0.25 * 5`).
        *   Introduce a constant, either globally (near `CLASS_WT`) or locally within `compute_scores`, for the bonus cap percentage: `NEW_BONUS_CAP_PERCENTAGE = 0.25`.
        *   Modify the line to use this constant: `max_bonus_points = core_weight * NEW_BONUS_CAP_PERCENTAGE * 5` (the `* 5` assumes max self-score, see next point).
        *   The existing logic for calculating `bonus_scale` and applying it to `df.loc[df["Classification"].isin(["Desirable", "Implicit"]), "RowScoreRaw"] *= bonus_scale` is the correct proportional scaling method for the new system and should be retained.

6.  **Introduce Global Constants for Key Scoring Parameters**
    *   **Why:** To improve readability, maintainability, and make scoring parameters explicit and easy to adjust if needed.
    *   **How:**
        *   At the top of the script (near `CLASS_WT`), define:
            ```python
            MAX_SELF_SCORE = 5
            # Max emphasis modifier is +0.5, so total multiplier is 1.5
            MAX_EMPHASIS_MULTIPLIER = 1.5
            THEORETICAL_MAX_RAW_SCORE_PER_ROW = CLASS_WT["Essential"] * MAX_EMPHASIS_MULTIPLIER * MAX_SELF_SCORE
            # This should calculate to 3.0 * 1.5 * 5 = 22.5
            ```
        *   In `load_matrix`, change `df["SelfScore"] = pd.to_numeric(df["SelfScore"], errors="coerce").fillna(0).clip(0, 5).astype(int)` to use the constant: `df["SelfScore"] = pd.to_numeric(df["SelfScore"], errors="coerce").fillna(0).clip(0, MAX_SELF_SCORE).astype(int)`.
        *   In `compute_scores`, update the `max_bonus_points` calculation if it explicitly used `5`: `max_bonus_points = core_weight * NEW_BONUS_CAP_PERCENTAGE * MAX_SELF_SCORE`.
        *   In `compute_scores`, change `df["RowScoreNorm"] = df["RowScoreRaw"] / 22.5` to use the constant: `df["RowScoreNorm"] = df["RowScoreRaw"] / THEORETICAL_MAX_RAW_SCORE_PER_ROW`.

7.  **Refine `core_gap_skills` Data Structure and Reporting in `main`**
    *   **Why:** To ensure the `core_gap_skills` list contains all necessary information in a consistent way and is reported clearly.
    *   **How:**
        *   In `compute_scores`, when populating `core_gap_skills`:
            *   The line `req_col = [col for col in df.columns if "requirement" in col.lower() or "skill" in col.lower()]` is okay, but ensure `req_col = req_col[0] if req_col else "Requirement"` correctly identifies the column name. It might be safer to assume the column is named "Requirement" as per your prompt.
            *   The current `core_gap_skills = df.loc[core_gap_mask, [req_col, "Classification", "SelfScore"]].to_dict('records')` is good.
        *   In `main()`, when printing core gap skills:
            *   Change the loop:
                ```python
                print("\n5. Core Gap Skills:") # Simplified title
                for skill_info in metrics["core_gap_skills"]:
                    # Assuming 'Requirement' is the key from to_dict('records')
                    # if req_col was 'Requirement'
                    req_name = skill_info.get("Requirement", skill_info.get(req_col, "N/A")) # Fallback if key varies
                    classification = skill_info.get("Classification", "N/A")
                    self_score = skill_info.get("SelfScore", "N/A")
                    print(f"   • \"{req_name}\" (Classification: {classification}, SelfScore: {self_score})")
                ```
            *   Adjust the descriptive text around core gaps in `main` to consistently refer to "Essential" or "Important" items based on the `CORE_GAP_THRESHOLDS` rather than "Weight 3" (e.g., the line `print("   ⚠️  At least one must-have skill (Weight 3) was self-scored 0 or 1.")` should be updated to reflect the new thresholds).

8.  **Update All Docstrings and Comments**
    *   **Why:** To accurately reflect the script's current functionality, focusing only on the new scoring system.
    *   **How:**
        *   Review and rewrite the main module docstring at the top of the file. Remove references to "Weight == 3 AND SelfScore ≤ 1" for core gaps, the old bonus cap logic, and the old usage examples. Describe the new system (Classification, Emphasis, 0-5 SelfScore, new core gap definitions, new bonus capping).
        *   Review and update the docstring for `load_matrix` to state it expects "Classification", "Requirement", and "SelfScore" columns.
        *   Review and update the docstring for `compute_scores` to describe the new scoring formula, the `CORE_GAP_THRESHOLDS`, and the new bonus capping mechanism.
        *   Remove any inline comments that refer to old logic, backward compatibility, or the `apply_bonus_cap` function.
        *   Update the `Usage` section in the main docstring to remove examples using `--cap`.

By following these steps, the script should be significantly simplified, focusing solely on the new, more nuanced scoring system.