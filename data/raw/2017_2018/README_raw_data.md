# Raw Data: NHANES 2017–2018 and Linked USDA Databases

This folder (`data/raw/2017_2018/`) holds the unmodified source files for the project. Nothing here is edited by hand; all cleaning happens in code and is saved to `data/clean/`.

## Sources

| Source | Publisher | Link |
|---|---|---|
| NHANES 2017–2018 | CDC, National Center for Health Statistics | https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2017 |
| FPED 2017–2018 | USDA, Food Surveys Research Group | https://www.ars.usda.gov/northeast-area/beltsville-md-bhnrc/beltsville-human-nutrition-research-center/food-surveys-research-group/docs/fped-databases/ |
| Flavonoid Database 2017–2018 | USDA, Food Surveys Research Group | https://www.ars.usda.gov/northeast-area/beltsville-md-bhnrc/beltsville-human-nutrition-research-center/food-surveys-research-group/docs/fndds-flavonoid-database/ |

Each NHANES file has a documentation page (same URL as the data file, ending in `.htm` instead of `.xpt`) listing every variable, its answer codes, and who was eligible.

## Conventions shared by all files

- **`SEQN`** is the participant ID and the merge key across every file (except `DRXFCD_J`, a food code lookup table).
- **Suffix `_J`** marks the 2017–2018 cycle.
- **Format:** NHANES files are SAS transport files (`.xpt`); USDA files are SAS datasets (`.sas7bdat`, extracted from `.exe` archives with 7-Zip). Both load with `pd.read_sas(path, encoding="utf-8")`.
- **Codes load as floats** (e.g., sex = `1.0`). Convert `SEQN` to `int` before merging.
- **Refused / Don't know** answers are stored as numeric codes (usually 7/9, 77/99, or 777/999) and must be recoded to missing per variable.
- **SAS zeros** sometimes load as tiny values like `5.4e-79`; treat these as 0.

## Demographics

### `DEMO_J` — Demographic variables and sample weights
Everyone in the 2017–2018 cycle (all ages). 550 were interviewed only and never examined, so they have no lab or exam data.

| Variable | Meaning | Use in project |
|---|---|---|
| `RIDAGEYR` | Age in years (top-coded at 80) | Control; adults 20+ filter |
| `RIAGENDR` | Sex (1 = male, 2 = female) | Control |
| `RIDRETH3` | Race/ethnicity, including NH Asian (1, 2, 3, 4, 6, 7) | Control |
| `DMDEDUC2` | Education, adults 20+ (1–5; 7, 9 = refused/don't know) | Control |
| `INDFMPIR` | Family income-to-poverty ratio (0–5, capped at 5) | Control|
| `RIDEXPRG` | Pregnancy status, women 20–44 (1 = pregnant, 2 = not, 3 = undetermined) | Exclusion |
| `RIDSTATR` | Interviewed only (1) or interviewed and examined (2) | Reference |
| `WTMEC2YR`, `SDMVPSU`, `SDMVSTRA` | Exam weight and survey design variables | Only needed for population-weighted estimates |

---

## Dietary

### `DR1IFF_J` / `DR2IFF_J` — Individual foods, recall days 1 and 2
One row per food or beverage reported in a 24-hour recall. Day 1 was collected in person; day 2 by phone 3–10 days later. Variable names are identical except for the `DR1`/`DR2` prefix.

| Variable | Meaning |
|---|---|
| `DR1DRSTZ` | Recall status (1 = reliable) |
| `DR1ILINE` | Food line number within the person's day |
| `DR1IFDCD` | 8-digit USDA food code (links to `DRXFCD_J`, FPED, FNDDS) |
| `DR1IGRMS` | Grams eaten |
| `DR1IKCAL`, `DR1IPROT`, `DR1ICARB`, … | ~65 nutrient values for that food, already scaled to grams eaten |
| `DR1_020` | Time eaten |
| `DR1_030Z` | Eating occasion (breakfast, lunch, dinner, snack, …) |
| `DR1FS` | Where the food came from (store, fast food, restaurant, …) |
| `DR1_040Z` | Eaten at home (1 = yes, 2 = no) |
| `DR1CCMNM` | Combination food number (links items eaten together, e.g., a sandwich) |

Summing a person's rows gives their daily nutrient intake.

### `DR1TOT_J` — Total nutrient intakes, day 1
One row per examined participant with day-1 nutrient totals (`DR1TKCAL`, `DR1TSODI`, …) plus recall status (`DR1DRSTZ`), dietary weights, and diet-behavior questions. Includes everyone examined, even those with unreliable recalls. Used to validate the sums computed from `DR1IFF_J`.

### `DRXFCD_J` — Food code descriptions
Lookup table of all 7,083 food codes in FNDDS 2017–2018. No `SEQN`.

| Variable | Meaning |
|---|---|
| `DRXFDCD` | 8-digit food code |
| `DRXFCSD` | Short description |
| `DRXFCLD` | Long description |

---

## Laboratory

| File | Key variable | Meaning | Eligibility |
|---|---|---|---|
| `GHB_J` | `LBXGH` | HbA1c, % (primary outcome) | Examined, ages 12+ |
| `HDL_J` | `LBDHDD` | HDL cholesterol, mg/dL | Examined, ages 6+ |
| `TCHOL_J` | `LBXTC` | Total cholesterol, mg/dL | Examined, ages 6+ |
| `HSCRP_J` | `LBXHSCRP` | High-sensitivity C-reactive protein, mg/L | Examined, nearly all ages |

The extra columns in `HDL_J`, `TCHOL_J`, and `HSCRP_J` are SI-unit versions or lab comment codes. 

---

## Examination

### `BMX_J` — Body measures
| Variable | Meaning |
|---|---|
| `BMXBMI` | Body mass index, kg/m² |
| `BMXWAIST` | Waist circumference, cm |
| `BMXWT`, `BMXHT` | Weight (kg), standing height (cm) |

### `BPX_J` — Blood pressure (manual cuff)
| Variable | Meaning |
|---|---|
| `BPXSY1`–`BPXSY4` | Systolic readings 1–4, mmHg |
| `BPXDI1`–`BPXDI4` | Diastolic readings 1–4, mmHg (a value of 0 is a measurement artifact) |

---

## Questionnaire

| File | Key variables | Meaning | Use |
|---|---|---|---|
| `DIQ_J` | `DIQ010` | Doctor told you have diabetes (1 = yes, 2 = no, 3 = borderline) | Exclusion |
| | `DIQ050` | Now taking insulin (1 = yes) | Exclusion |
| | `DIQ070` | Now taking diabetic pills (1 = yes) | Exclusion |
| `SMQ_J` | `SMQ020` | Smoked at least 100 cigarettes in life | Control (smoking status) |
| | `SMQ040` | Now smoke (1 = every day, 2 = some days, 3 = not at all) | Control (smoking status) |
| `PAQ_J` | `PAQ605`, `PAQ620` | Vigorous / moderate work activity | Control (physical activity) |
| | `PAQ635` | Walk or bicycle for transportation | Control (physical activity) |
| | `PAQ650`, `PAQ665` | Vigorous / moderate recreational activity | Control (physical activity) |
| `FSQ_J` | `FSDHH` | Household food security (1 = full, 2 = marginal, 3 = low, 4 = very low) | Control |

`SMQ_J` and `PAQ_J` cover adults only; see their documentation pages for exact age ranges.

---

## USDA linked files

These are participant-level daily totals computed by USDA from the same NHANES recalls, so they merge on `SEQN`. Each has a day-1 and a day-2 file with identical structure except the `DR1T`/`DR2T` prefix.

### FPED intake totals (`fped_dr1tot_1718`, `fped_dr2tot_1718`)
Converts each person's foods into **37 USDA Food Patterns components**: cup-equivalents of fruit, vegetables, and dairy; ounce-equivalents of grains and protein foods; teaspoon-equivalents of added sugars; gram-equivalents of oils and solid fats; and number of alcoholic drinks.

| Group | Example columns |
|---|---|
| Fruit | `DR1T_F_TOTAL`, `DR1T_F_CITMLB`, `DR1T_F_JUICE` |
| Vegetables | `DR1T_V_TOTAL`, `DR1T_V_DRKGR`, `DR1T_V_LEGUMES` |
| Grains | `DR1T_G_TOTAL`, `DR1T_G_WHOLE`, `DR1T_G_REFINED` |
| Protein foods | `DR1T_PF_MEAT`, `DR1T_PF_CUREDMEAT`, `DR1T_PF_SEAFD_HI`, `DR1T_PF_NUTSDS` |
| Dairy | `DR1T_D_TOTAL`, `DR1T_D_MILK`, `DR1T_D_CHEESE` |
| Other | `DR1T_OILS`, `DR1T_SOLID_FATS`, `DR1T_ADD_SUGARS`, `DR1T_A_DRINKS` |

Also contains copies of demographic variables, weights, recall status (`DR1DRSTZ`), and `DR1TNUMF` (number of foods reported, not a food group).

### Flavonoid intake totals (`flav_dr1tot_1718`, `flav_dr2tot_1718`)
Daily intake (mg) of **29 individual flavonoids**, **6 flavonoid classes**, and total flavonoids. Column names load in lowercase.

| Columns | Meaning |
|---|---|
| `dr1t_fl710` … `dr1t_fl794` | 29 individual flavonoids, labeled by USDA nutrient number (e.g., 710–712 = soy isoflavones; 789 = quercetin). Names are in the documentation file extracted with the data. |
| `dr1t_fl_iso`, `_antho`, `_3_ols`, `_nones`, `_ones`, `_ols` | Class totals: isoflavones, anthocyanidins, flavan-3-ols, flavanones, flavones, flavonols |
| `dr1t_fl_catechin` | Catechin subtotal |
| `dr1t_fl_total` | Total flavonoids |

About 90% of non-zero values in the underlying database are imputed from similar foods rather than directly measured (USDA documentation).
