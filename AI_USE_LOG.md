# AI Use Log

DS 6021 Final Project: *Do Nutrition Labels Show the Right Information?*

This log records how generative AI (Claude, Anthropic) was used in building the dataset, which code it produced, and how that code was tested. It covers the data-construction stage (October 14-17, 2026). Add new entries as the project continues.

## How AI was used

- **Code generation.** All code in `combining.ipynb` should be treated as AI-generated: Claude drafted it, and I reviewed, tested and adapted it.
- **Explanation.** I asked Claude to explain the code line by line before using it (merges, pivots, `.where`, `axis=0` vs `axis=1`, `groupby`, and so on). After the first few cells I asked for code without explanatory comments so that I would read it and write my own.
- **Planning and review.** Claude helped check the plan against the rubric, discussed the modeling and clustering design, and flagged data issues.

## AI-generated code and how it was tested

| # | Cell | What it does | How I tested it | My changes |
|---|---|---|---|---|
| 1 | Column inspection | Prints types and first rows of FPED, flavonoid and IFF tables | Read output; confirmed join keys and prefixes | None |
| 2 | FPED lookup | Drops description, strips unit labels from column names | `assert FOODCODE.is_unique`; shape (7083, 38) | Kept units in a separate lookup |
| 3 | Flavonoid lookup | Pivots long table (262,071 rows) to wide, names columns | Pivot fails on duplicates; asserts no missing names or values; totals equal sum of 29 compounds | Found that 18 columns were named `nan` (USDA left TAGNAME blank); Claude supplied names |
| 4 | Stack recall days | Strips `DR1`/`DR2` prefixes, stacks days, keeps reliable recalls | Asserts both days have identical columns after stripping, no duplicate columns | Wrote my own comments |
| 5 | Join and scale | Joins FPED and flavonoids by food code, multiplies by grams / 100 | `validate="m:1"`; 0 unmatched food codes in either join | None |
| 6 | Calorie check | Sums food-level kcal per person, compares with USDA `DR1TOT` | Max difference near 0 | None |
| 7 | Validation vs USDA totals | Compares all 74 food-group and flavonoid daily sums with USDA's published person-day totals, both days | Food groups within 0.04; flavonoids within 0.4 mg (rounding of per-100 g values); 0 people missing from official totals | Asked for relative-difference check to rule out mapping errors |
| 8 | Person-level diet | Daily totals, two-day means, per-1,000-kcal versions, plausibility flag | Checked shape (7,495 x 280), day counts, sample rows by hand | Changed rule to require plausible energy on **both** days; removed day-1-only column |
| 9 | Person details | Demographics, outcomes, smoking, physical activity, diabetes flags; joins 10 tables | `validate="1:1"` on every join; missing counts reconciled with source file sizes (e.g. 3,398 not in PAQ + 52 + 79 = 3,529) | Dropped income bins and HbA1c categories; asked for a better activity measure (MET-minutes) |
| 10 | Exclusion cascade | Applies 7 exclusion steps in order, counts removals | First 6 steps match my earlier independent pass exactly (5,569 / 5,018 / 4,561 / 4,518 / 3,790 / 3,730) | Chose calorie cutoffs |
| 11 | Save CSVs | Writes raw and processed tables; gzip for the food-level table | Checked file sizes and that files exist | None |
| 12 | Load fix | Sets numeric values below 1e-30 to exactly 0 in `read()` | Minimum of `SED_MIN` went from 5.4e-79 to 0; earlier validation unchanged | Added to my own function |

## Decisions I made

- **Plausible-calorie rule:** required plausible intake on every reliable recall day, not just day 1 (Claude had suggested dropping only an implausible day 2). Cost: 166 more people excluded than a day-1-only rule.
- **Calorie cutoffs:** standard Willett limits (women 500-3,500 kcal, men 800-4,200 kcal) after testing looser limits (4,500 / 5,000).
- **Day-1 requirement dropped:** any reliable recall day qualifies.
- **No classification outcome:** HbA1c is modeled as continuous; Claude initially overstated the rubric's classification requirement and corrected this after I checked.
- **Income kept continuous:** handling of the ~11% missing income values deferred to modeling.
- **Physical activity:** weekly MET-minutes (WHO GPAQ weights, 16-hour/day cleaning rule) instead of a yes/no "active" flag, with no additional 180-minute cap.

## Problems caught during review

- 18 flavonoid columns had no name after the pivot (blank `TAGNAME` in USDA's file). Caught from `flav.info()` output; fixed and guarded with an `assert`.
- `pd.read_sas` read some zeros as 5.4e-79, which would have let diastolic readings of 0 escape the `replace(0, nan)` step. Caught from `describe()` output; fixed at load.
- Claude predicted 2,853 missing HbA1c values; the actual 3,209 includes 356 people with a GHB record but no result. No code change needed.
- A `PerformanceWarning` (fragmented DataFrame) was harmless; fixed with `.copy()`.

## Overall verification

The strongest test is external: daily totals rebuilt from individual foods match USDA's independently published totals for calories, all 37 food groups and all 37 flavonoids, for every participant on both recall days. The exclusion cascade reproduces an earlier independent pass at every step except the deliberately changed calorie rule.
