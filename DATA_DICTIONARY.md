# Data Dictionary: `analytic_cohort.csv`

One row per participant in the final modeling cohort: **3,286 adults** from NHANES 2017-2018, **305 columns**. Built in `combining.ipynb`. A machine-readable version of this table is in `data_dictionary.csv`.

## Cohort

| Step | Removed | Remaining |
|---|---|---|
| All NHANES 2017-2018 participants |  | 9,254 |
| Adults 20+ | 3,685 | 5,569 |
| Has HbA1c | 551 | 5,018 |
| Reliable dietary recall (at least one day) | 457 | 4,561 |
| Not pregnant | 43 | 4,518 |
| No diagnosed diabetes (DIQ010 == 1) | 728 | 3,790 |
| No insulin or diabetes pills | 60 | 3,730 |
| Plausible energy on every recall day (Willett cutoffs) | 444 | 3,286 |

## Conventions

- **Missing values** are blank (`NaN`). NHANES refused / don't-know codes (7/9, 77/99, 7777/9999) were recoded to missing.
- **Near-zero artifacts**: `pd.read_sas` reads some true zeros as ~5.4e-79; all numeric values with |x| < 1e-30 were set to exactly 0 at load.
- **Diet columns** come from 24-hour recalls. Each food was linked by its 8-digit USDA food code to FPED and the Flavonoid Database, scaled by grams eaten, and summed to daily totals. Daily totals were averaged across reliable recall days. Summed totals were validated against USDA's published person-day totals (calories exact; food groups within 0.04; flavonoids within 0.4 mg).
- **`_P1K` columns** are density versions: the daily mean divided by mean energy intake in thousands of kcal. `KCAL` has no `_P1K` version.
- **Flavonoid totals** (`FL_TOT_*`) are exact sums of their component compounds. Use either totals or compounds in a model, not both.
- About 90% of non-zero flavonoid values in the USDA database are imputed rather than directly measured.

## Column groups

| Group | Columns |
|---|---|
| Identifier | 1 |
| Demographics (controls) | 6 |
| Outcomes | 8 |
| Lifestyle (controls) | 5 |
| Diabetes questionnaire (exclusion inputs) | 3 |
| Exclusion flags | 3 |
| Diet: recall summary | 2 |
| Diet: nutrients (daily) | 65 |
| Diet: food groups (daily) | 37 |
| Diet: flavonoids (daily) | 37 |
| Diet: nutrients per 1,000 kcal | 64 |
| Diet: food groups per 1,000 kcal | 37 |
| Diet: flavonoids per 1,000 kcal | 37 |
| **Total** | **305** |


## Identifier

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `SEQN` | NHANES respondent sequence number; unique participant ID and the join key for every table. |  | DEMO_J | Integer. One row per SEQN in this table. |

## Demographics (controls)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `RIDAGEYR` | Age in years at screening. | years | DEMO_J | Top-coded at 80 (80 = 80 or older). Cohort restricted to 20+. |
| `RIAGENDR` | Sex. | code | DEMO_J | 1 = Male, 2 = Female. |
| `RIDRETH3` | Race/Hispanic origin with Non-Hispanic Asian category. | code | DEMO_J | 1 = Mexican American, 2 = Other Hispanic, 3 = Non-Hispanic White, 4 = Non-Hispanic Black, 6 = Non-Hispanic Asian, 7 = Other race (incl. multiracial). Categorical: one-hot encode for modeling; there is no code 5. |
| `DMDEDUC2` | Highest education level (adults 20+). | code | DEMO_J | 1 = Less than 9th grade, 2 = 9th-11th grade (incl. 12th with no diploma), 3 = High school graduate/GED, 4 = Some college or AA degree, 5 = College graduate or above. Refused (7) and Don't know (9) recoded to missing. |
| `INDFMPIR` | Ratio of family income to the federal poverty guideline. | ratio | DEMO_J | Continuous 0-5; values of 5 or more are top-coded as 5. About 11% missing in the cohort; handling (missing indicator, bins or imputation) is decided at modeling time. |
| `RIDEXPRG` | Pregnancy status at exam (women 20-44 only). | code | DEMO_J | 1 = Pregnant (positive urine test or self-report), 2 = Not pregnant, 3 = Could not be determined. Missing for men and women outside the age range. Used only to build PREGNANT. |

## Outcomes

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `LBXGH` | Glycohemoglobin (HbA1c). Primary outcome. | % | GHB_J | Clinical reference: < 5.7 normal, 5.7-6.4 prediabetes range, >= 6.5 diabetes range. Required non-missing for inclusion. |
| `LBDHDD` | Direct HDL cholesterol. | mg/dL | HDL_J | Higher is generally favorable. |
| `LBXTC` | Total cholesterol. | mg/dL | TCHOL_J |  |
| `LBXHSCRP` | High-sensitivity C-reactive protein (inflammation marker). | mg/L | HSCRP_J | Strongly right-skewed; consider log transform. Values > 10 mg/L often reflect acute infection. |
| `BMXBMI` | Body mass index. | kg/m^2 | BMX_J | Treated as an outcome, not a control (diet affects it). |
| `BMXWAIST` | Waist circumference. | cm | BMX_J | Treated as an outcome, not a control. |
| `SBP` | Mean systolic blood pressure across available readings. | mm Hg | BPX_J (derived) | Mean of BPXSY1-BPXSY4, skipping missing readings. Missing if no valid reading. |
| `DBP` | Mean diastolic blood pressure across available readings. | mm Hg | BPX_J (derived) | Mean of BPXDI1-BPXDI4; readings of 0 (pulse audible to zero) set to missing before averaging. |

## Lifestyle (controls)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `SMOKING` | Cigarette smoking status. | category | SMQ_J (derived) | 'never' = SMQ020 == 2 (fewer than 100 cigarettes in life); 'former' = SMQ020 == 1 and SMQ040 == 3 (not at all now); 'current' = SMQ040 in {1, 2} (every day or some days). Refused/Don't know recoded to missing before deriving. |
| `MET_MIN_WK` | Total weekly physical activity in MET-minutes. | MET-min/week | PAQ_J (derived) | Sum over 5 domains of days/week x minutes/day x MET weight (vigorous work 8, moderate work 4, walk/bike for transport 4, vigorous recreation 8, moderate recreation 4; WHO GPAQ guide). 'No' to a domain = 0. Missing if any domain is unknown, or if reported activity exceeds 960 min/day (GPAQ cleaning rule; 79 people). Right-skewed: use log1p or MEETS_PA in models. |
| `MEETS_PA` | Meets the physical activity guideline (>= 600 MET-min/week, about 150 min moderate). | 0/1 | PAQ_J (derived) | 1 = MET_MIN_WK >= 600, 0 = below, missing when MET_MIN_WK is missing. |
| `SED_MIN` | Minutes of sedentary activity (sitting) on a typical day. | min/day | PAQ_J (PAD680) | Refused (7777) and Don't know (9999) recoded to missing. No upper cap applied; max 1,320. |
| `FSDHH` | Household food security category (past 12 months). | code | FSQ_J | 1 = Full, 2 = Marginal, 3 = Low, 4 = Very low food security. Ordinal. |

## Diabetes questionnaire (exclusion inputs)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `DIQ010` | Doctor told you have diabetes. | code | DIQ_J | 1 = Yes, 2 = No, 3 = Borderline. Refused/Don't know to missing. Cohort contains only 2, 3 or missing (1 excluded). |
| `DIQ050` | Now taking insulin. | code | DIQ_J | 1 = Yes, 2 = No. Refused/Don't know to missing. Cohort contains no 1s. |
| `DIQ070` | Now taking diabetic pills to lower blood sugar. | code | DIQ_J | 1 = Yes, 2 = No. Asked only of people reporting diabetes/prediabetes, so mostly missing by design (skip pattern). Cohort contains no 1s. |

## Exclusion flags

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `PREGNANT` | Pregnant at exam. | True/False | derived | RIDEXPRG == 1. All False in the cohort. |
| `DIABETES_DX` | Diagnosed diabetes. | True/False | derived | DIQ010 == 1. All False in the cohort (borderline kept). |
| `DIABETES_MED` | Taking insulin or diabetes pills. | True/False | derived | DIQ050 == 1 or DIQ070 == 1. All False in the cohort. |

## Diet: recall summary

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `N_DAYS` | Number of reliable dietary recall days used in the diet averages. | days | DR1IFF_J / DR2IFF_J (derived) | 1 or 2. Reliable = recall status DR?DRSTZ == 1. One-day averages are noisier than two-day averages. |
| `PLAUSIBLE_ALL` | Energy intake plausible on every reliable recall day. | True/False | derived | Plausible = 500-3,500 kcal/day (women) or 800-4,200 kcal/day (men), Willett cutoffs, checked separately on each day. All True in the cohort. |

## Diet: nutrients (daily)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `KCAL` | Energy. | kcal/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `PROT` | Protein. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CARB` | Carbohydrate. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `SUGR` | Total sugars. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `FIBE` | Dietary fiber. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `TFAT` | Total fat. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `SFAT` | Total saturated fatty acids. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `MFAT` | Total monounsaturated fatty acids. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `PFAT` | Total polyunsaturated fatty acids. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CHOL` | Cholesterol. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `ATOC` | Vitamin E as alpha-tocopherol. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `ATOA` | Added alpha-tocopherol (vitamin E). | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `RET` | Retinol. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VARA` | Vitamin A, RAE. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `ACAR` | Alpha-carotene. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `BCAR` | Beta-carotene. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CRYP` | Beta-cryptoxanthin. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `LYCO` | Lycopene. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `LZ` | Lutein + zeaxanthin. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VB1` | Thiamin (vitamin B1). | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VB2` | Riboflavin (vitamin B2). | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `NIAC` | Niacin. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VB6` | Vitamin B6. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `FOLA` | Total folate. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `FA` | Folic acid. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `FF` | Food folate. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `FDFE` | Folate, DFE (dietary folate equivalents). | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CHL` | Total choline. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VB12` | Vitamin B12. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `B12A` | Added vitamin B12. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VC` | Vitamin C. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VD` | Vitamin D (D2 + D3). | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `VK` | Vitamin K. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CALC` | Calcium. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `PHOS` | Phosphorus. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `MAGN` | Magnesium. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `IRON` | Iron. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `ZINC` | Zinc. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `COPP` | Copper. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `SODI` | Sodium. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `POTA` | Potassium. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `SELE` | Selenium. | mcg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `CAFF` | Caffeine. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `THEO` | Theobromine. | mg/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `ALCO` | Alcohol. | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `MOIS` | Moisture (water in foods and beverages). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S040` | Saturated fatty acid 4:0 (butanoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S060` | Saturated fatty acid 6:0 (hexanoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S080` | Saturated fatty acid 8:0 (octanoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S100` | Saturated fatty acid 10:0 (decanoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S120` | Saturated fatty acid 12:0 (dodecanoic / lauric). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S140` | Saturated fatty acid 14:0 (tetradecanoic / myristic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S160` | Saturated fatty acid 16:0 (hexadecanoic / palmitic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `S180` | Saturated fatty acid 18:0 (octadecanoic / stearic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `M161` | Monounsaturated fatty acid 16:1 (hexadecenoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `M181` | Monounsaturated fatty acid 18:1 (octadecenoic / oleic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `M201` | Monounsaturated fatty acid 20:1 (eicosenoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `M221` | Monounsaturated fatty acid 22:1 (docosenoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P182` | Polyunsaturated fatty acid 18:2 (octadecadienoic / linoleic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P183` | Polyunsaturated fatty acid 18:3 (octadecatrienoic / linolenic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P184` | Polyunsaturated fatty acid 18:4 (octadecatetraenoic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P204` | Polyunsaturated fatty acid 20:4 (eicosatetraenoic / arachidonic). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P205` | Polyunsaturated fatty acid 20:5 (eicosapentaenoic / EPA). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P225` | Polyunsaturated fatty acid 22:5 (docosapentaenoic / DPA). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |
| `P226` | Polyunsaturated fatty acid 22:6 (docosahexaenoic / DHA). | g/day | DR1IFF_J / DR2IFF_J (DR?I<name>) | Two-day mean of daily totals (one-day value if N_DAYS = 1). Pre-scaled to grams eaten by NHANES; summed per day. |

## Diet: food groups (daily)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `F_TOTAL` | Total fruit (citrus, melons, berries, other fruit and juice). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `F_CITMLB` | Citrus, melons and berries. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `F_OTHER` | Other fruits (excluding citrus, melons, berries). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `F_JUICE` | 100% fruit juice. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_TOTAL` | Total vegetables (excluding legumes). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_DRKGR` | Dark green vegetables. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_REDOR_TOTAL` | Total red and orange vegetables. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_REDOR_TOMATO` | Tomatoes and tomato products. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_REDOR_OTHER` | Other red and orange vegetables (excluding tomatoes). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_STARCHY_TOTAL` | Total starchy vegetables. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_STARCHY_POTATO` | White potatoes. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_STARCHY_OTHER` | Other starchy vegetables (excluding white potatoes). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_OTHER` | Other vegetables not in the vegetable components above. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `V_LEGUMES` | Beans, peas and lentils counted as vegetables. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `G_TOTAL` | Total grains. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `G_WHOLE` | Whole grains. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `G_REFINED` | Refined grains. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_TOTAL` | Total protein foods. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_MPS_TOTAL` | Total meat, poultry, organ meat, cured meat and seafood. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_MEAT` | Beef, veal, pork, lamb and game (excluding organ and cured meat). | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_CUREDMEAT` | Cured or processed meats (frankfurters, sausages, bacon, luncheon meats). | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_ORGAN` | Organ meats. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_POULT` | Poultry (chicken, turkey, other). | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_SEAFD_HI` | Seafood high in n-3 fatty acids. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_SEAFD_LOW` | Seafood low in n-3 fatty acids. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_EGGS` | Eggs (chicken, duck, goose, quail) and egg substitutes. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_SOY` | Soy products (excluding soy milk and calcium-fortified soy products). | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_NUTSDS` | Nuts and seeds. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `PF_LEGUMES` | Beans, peas and lentils counted as protein foods. | oz eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `D_TOTAL` | Total dairy (milk, yogurt, cheese, fortified soy milk). | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `D_MILK` | Fluid milk, buttermilk, evaporated/dry milk and calcium-fortified soy milk. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `D_YOGURT` | Yogurt. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `D_CHEESE` | Cheese. | cup eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `OILS` | Fats naturally present in nuts, seeds, seafood; unhydrogenated vegetable oils; soft margarines. | g/day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `SOLID_FATS` | Fats naturally present in meat, poultry, eggs, dairy; lard, tallow, butter; hydrogenated oils. | g/day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `ADD_SUGARS` | Added sugars (foods as consumed). | tsp eq./day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |
| `A_DRINKS` | Alcoholic drinks. | no. of drinks/day | USDA FPED 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g FPED value x grams eaten / 100, summed per day. Validated against USDA FPED day totals (max diff 0.04). |

## Diet: flavonoids (daily)

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `FL_DAIDZN` | Daidzein. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 710; class: Isoflavone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_GNSTEIN` | Genistein. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 711; class: Isoflavone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_GLYCTEIN` | Glycitein. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 712; class: Isoflavone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_CYAD` | Cyanidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 731; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_PETUNIDIN` | Petunidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 740; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_DELPH` | Delphinidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 741; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_MALVIDIN` | Malvidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 742; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_PELARGON` | Pelargonidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 743; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_PEONIDIN` | Peonidin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 745; class: Anthocyanidin. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_CATECHIN` | (+)-Catechin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 749; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_EPICATEGC` | (-)-Epigallocatechin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 750; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_EPICATEC` | (-)-Epicatechin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 751; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_EPICATECG3` | (-)-Epicatechin 3-gallate. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 752; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_EGCG` | (-)-Epigallocatechin 3-gallate. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 753; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_THEAFLAV` | Theaflavin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 755; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_THEARUBIG` | Thearubigins. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 756; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_ERIODICT` | Eriodictyol. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 758; class: Flavanone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_HESPT` | Hesperetin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 759; class: Flavanone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_NARING` | Naringenin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 762; class: Flavanone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_APIGEN` | Apigenin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 770; class: Flavone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_LUTEOL` | Luteolin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 773; class: Flavone. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_ISORHAM` | Isorhamnetin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 785; class: Flavonol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_KAEMF` | Kaempferol. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 786; class: Flavonol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_MYRIC` | Myricetin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 788; class: Flavonol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_QUERCE` | Quercetin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 789; class: Flavonol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_THEAFLAV33DG` | Theaflavin-3,3'-digallate. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 791; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_THEAFLAV3PG` | Theaflavin-3'-gallate. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 792; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_THEAFLAV3G` | Theaflavin-3-gallate. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 793; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_GALCATEGC` | (+)-Gallocatechin. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 794; class: Flavan-3-ol. Validated against USDA flavonoid day totals (max diff 0.4 mg). |
| `FL_TOT_FLAVONOIDS` | Total flavonoids (sum of all 29 compounds). | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7000; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_ANTHOCYAN` | Total anthocyanidins. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7100; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_CATECHINS` | Total catechins (monomeric flavan-3-ols only). | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7200; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_FLAVAN3OL` | Total flavan-3-ols (catechins plus theaflavins and thearubigins). | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7300; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_FLAVANONE` | Total flavanones. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7400; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_FLAVONE` | Total flavones. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7500; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_FLAVONOL` | Total flavonols. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7600; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |
| `FL_TOT_ISOFLAV` | Total isoflavones. | mg/day | USDA Flavonoid Database 2017-2018 | Two-day mean of daily totals (one-day value if N_DAYS = 1). Per-100 g value x grams / 100, summed per day. USDA nutrient code 7700; class: Total. Validated against USDA flavonoid day totals (max diff 0.4 mg). Exact sum of its component compounds: do not model together with them. |

## Diet: nutrients per 1,000 kcal

Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten.

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `PROT_P1K` | Protein, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CARB_P1K` | Carbohydrate, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `SUGR_P1K` | Total sugars, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FIBE_P1K` | Dietary fiber, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `TFAT_P1K` | Total fat, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `SFAT_P1K` | Total saturated fatty acids, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `MFAT_P1K` | Total monounsaturated fatty acids, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PFAT_P1K` | Total polyunsaturated fatty acids, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CHOL_P1K` | Cholesterol, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ATOC_P1K` | Vitamin E as alpha-tocopherol, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ATOA_P1K` | Added alpha-tocopherol (vitamin E), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `RET_P1K` | Retinol, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VARA_P1K` | Vitamin A, RAE, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ACAR_P1K` | Alpha-carotene, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `BCAR_P1K` | Beta-carotene, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CRYP_P1K` | Beta-cryptoxanthin, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `LYCO_P1K` | Lycopene, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `LZ_P1K` | Lutein + zeaxanthin, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VB1_P1K` | Thiamin (vitamin B1), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VB2_P1K` | Riboflavin (vitamin B2), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `NIAC_P1K` | Niacin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VB6_P1K` | Vitamin B6, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FOLA_P1K` | Total folate, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FA_P1K` | Folic acid, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FF_P1K` | Food folate, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FDFE_P1K` | Folate, DFE (dietary folate equivalents), per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CHL_P1K` | Total choline, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VB12_P1K` | Vitamin B12, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `B12A_P1K` | Added vitamin B12, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VC_P1K` | Vitamin C, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VD_P1K` | Vitamin D (D2 + D3), per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `VK_P1K` | Vitamin K, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CALC_P1K` | Calcium, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PHOS_P1K` | Phosphorus, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `MAGN_P1K` | Magnesium, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `IRON_P1K` | Iron, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ZINC_P1K` | Zinc, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `COPP_P1K` | Copper, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `SODI_P1K` | Sodium, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `POTA_P1K` | Potassium, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `SELE_P1K` | Selenium, per 1,000 kcal. | mcg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `CAFF_P1K` | Caffeine, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `THEO_P1K` | Theobromine, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ALCO_P1K` | Alcohol, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `MOIS_P1K` | Moisture (water in foods and beverages), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S040_P1K` | Saturated fatty acid 4:0 (butanoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S060_P1K` | Saturated fatty acid 6:0 (hexanoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S080_P1K` | Saturated fatty acid 8:0 (octanoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S100_P1K` | Saturated fatty acid 10:0 (decanoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S120_P1K` | Saturated fatty acid 12:0 (dodecanoic / lauric), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S140_P1K` | Saturated fatty acid 14:0 (tetradecanoic / myristic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S160_P1K` | Saturated fatty acid 16:0 (hexadecanoic / palmitic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `S180_P1K` | Saturated fatty acid 18:0 (octadecanoic / stearic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `M161_P1K` | Monounsaturated fatty acid 16:1 (hexadecenoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `M181_P1K` | Monounsaturated fatty acid 18:1 (octadecenoic / oleic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `M201_P1K` | Monounsaturated fatty acid 20:1 (eicosenoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `M221_P1K` | Monounsaturated fatty acid 22:1 (docosenoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P182_P1K` | Polyunsaturated fatty acid 18:2 (octadecadienoic / linoleic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P183_P1K` | Polyunsaturated fatty acid 18:3 (octadecatrienoic / linolenic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P184_P1K` | Polyunsaturated fatty acid 18:4 (octadecatetraenoic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P204_P1K` | Polyunsaturated fatty acid 20:4 (eicosatetraenoic / arachidonic), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P205_P1K` | Polyunsaturated fatty acid 20:5 (eicosapentaenoic / EPA), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P225_P1K` | Polyunsaturated fatty acid 22:5 (docosapentaenoic / DPA), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `P226_P1K` | Polyunsaturated fatty acid 22:6 (docosahexaenoic / DHA), per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |

## Diet: food groups per 1,000 kcal

Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten.

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `F_TOTAL_P1K` | Total fruit (citrus, melons, berries, other fruit and juice), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `F_CITMLB_P1K` | Citrus, melons and berries, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `F_OTHER_P1K` | Other fruits (excluding citrus, melons, berries), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `F_JUICE_P1K` | 100% fruit juice, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_TOTAL_P1K` | Total vegetables (excluding legumes), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_DRKGR_P1K` | Dark green vegetables, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_REDOR_TOTAL_P1K` | Total red and orange vegetables, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_REDOR_TOMATO_P1K` | Tomatoes and tomato products, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_REDOR_OTHER_P1K` | Other red and orange vegetables (excluding tomatoes), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_STARCHY_TOTAL_P1K` | Total starchy vegetables, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_STARCHY_POTATO_P1K` | White potatoes, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_STARCHY_OTHER_P1K` | Other starchy vegetables (excluding white potatoes), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_OTHER_P1K` | Other vegetables not in the vegetable components above, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `V_LEGUMES_P1K` | Beans, peas and lentils counted as vegetables, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `G_TOTAL_P1K` | Total grains, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `G_WHOLE_P1K` | Whole grains, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `G_REFINED_P1K` | Refined grains, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_TOTAL_P1K` | Total protein foods, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_MPS_TOTAL_P1K` | Total meat, poultry, organ meat, cured meat and seafood, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_MEAT_P1K` | Beef, veal, pork, lamb and game (excluding organ and cured meat), per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_CUREDMEAT_P1K` | Cured or processed meats (frankfurters, sausages, bacon, luncheon meats), per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_ORGAN_P1K` | Organ meats, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_POULT_P1K` | Poultry (chicken, turkey, other), per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_SEAFD_HI_P1K` | Seafood high in n-3 fatty acids, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_SEAFD_LOW_P1K` | Seafood low in n-3 fatty acids, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_EGGS_P1K` | Eggs (chicken, duck, goose, quail) and egg substitutes, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_SOY_P1K` | Soy products (excluding soy milk and calcium-fortified soy products), per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_NUTSDS_P1K` | Nuts and seeds, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `PF_LEGUMES_P1K` | Beans, peas and lentils counted as protein foods, per 1,000 kcal. | oz eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `D_TOTAL_P1K` | Total dairy (milk, yogurt, cheese, fortified soy milk), per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `D_MILK_P1K` | Fluid milk, buttermilk, evaporated/dry milk and calcium-fortified soy milk, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `D_YOGURT_P1K` | Yogurt, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `D_CHEESE_P1K` | Cheese, per 1,000 kcal. | cup eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `OILS_P1K` | Fats naturally present in nuts, seeds, seafood; unhydrogenated vegetable oils; soft margarines, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `SOLID_FATS_P1K` | Fats naturally present in meat, poultry, eggs, dairy; lard, tallow, butter; hydrogenated oils, per 1,000 kcal. | g per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `ADD_SUGARS_P1K` | Added sugars (foods as consumed), per 1,000 kcal. | tsp eq. per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `A_DRINKS_P1K` | Alcoholic drinks, per 1,000 kcal. | no. of drinks per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |

## Diet: flavonoids per 1,000 kcal

Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten.

| Column | Description | Units | Source | Notes |
|---|---|---|---|---|
| `FL_DAIDZN_P1K` | Daidzein, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_GNSTEIN_P1K` | Genistein, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_GLYCTEIN_P1K` | Glycitein, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_CYAD_P1K` | Cyanidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_PETUNIDIN_P1K` | Petunidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_DELPH_P1K` | Delphinidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_MALVIDIN_P1K` | Malvidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_PELARGON_P1K` | Pelargonidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_PEONIDIN_P1K` | Peonidin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_CATECHIN_P1K` | (+)-Catechin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_EPICATEGC_P1K` | (-)-Epigallocatechin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_EPICATEC_P1K` | (-)-Epicatechin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_EPICATECG3_P1K` | (-)-Epicatechin 3-gallate, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_EGCG_P1K` | (-)-Epigallocatechin 3-gallate, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_THEAFLAV_P1K` | Theaflavin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_THEARUBIG_P1K` | Thearubigins, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_ERIODICT_P1K` | Eriodictyol, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_HESPT_P1K` | Hesperetin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_NARING_P1K` | Naringenin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_APIGEN_P1K` | Apigenin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_LUTEOL_P1K` | Luteolin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_ISORHAM_P1K` | Isorhamnetin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_KAEMF_P1K` | Kaempferol, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_MYRIC_P1K` | Myricetin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_QUERCE_P1K` | Quercetin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_THEAFLAV33DG_P1K` | Theaflavin-3,3'-digallate, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_THEAFLAV3PG_P1K` | Theaflavin-3'-gallate, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_THEAFLAV3G_P1K` | Theaflavin-3-gallate, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_GALCATEGC_P1K` | (+)-Gallocatechin, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_FLAVONOIDS_P1K` | Total flavonoids (sum of all 29 compounds), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_ANTHOCYAN_P1K` | Total anthocyanidins, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_CATECHINS_P1K` | Total catechins (monomeric flavan-3-ols only), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_FLAVAN3OL_P1K` | Total flavan-3-ols (catechins plus theaflavins and thearubigins), per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_FLAVANONE_P1K` | Total flavanones, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_FLAVONE_P1K` | Total flavones, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_FLAVONOL_P1K` | Total flavonols, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |
| `FL_TOT_ISOFLAV_P1K` | Total isoflavones, per 1,000 kcal. | mg per 1,000 kcal | derived | Per 1,000 kcal: the two-day mean divided by mean KCAL / 1000. Describes diet composition independent of amount eaten. |

## Checking this dictionary against the data

```python
import pandas as pd
cohort = pd.read_csv("data/processed/analytic_cohort.csv")
dd = pd.read_csv("data_dictionary.csv")
assert list(cohort.columns) == list(dd["column"]), set(cohort.columns) ^ set(dd["column"])
```
