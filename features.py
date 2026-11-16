import pandas as pd

def add_derived(df):
    df = df.copy()
    df["LEGUMES_P1K"] = df["V_LEGUMES_P1K"]
    df["MARINE_N3_P1K"] = df["P205_P1K"] + df["P225_P1K"] + df["P226_P1K"]
    df["NATURAL_SUGR_P1K"] = (df["SUGR_P1K"] - 4.2 * df["ADD_SUGARS_P1K"]).clip(lower=0)
    df["F_WHOLE_P1K"] = df["F_CITMLB_P1K"] + df["F_OTHER_P1K"]
    df["VEG_OTHER_NS_P1K"] = df["V_REDOR_TOTAL_P1K"] + df["V_OTHER_P1K"]
    return df

LABEL = ["TFAT", "SFAT", "CHOL", "SODI", "CARB", "FIBE", "SUGR", "ADD_SUGARS",
         "PROT", "VD", "CALC", "IRON", "POTA"]

HEURISTIC = ["VEG_OTHER_NS", "G_WHOLE", "G_REFINED", "ADD_SUGARS", "F_WHOLE", "V_DRKGR", "LEGUMES",
             "PF_NUTSDS", "PF_MEAT", "PF_CUREDMEAT", "D_YOGURT", "PF_SEAFD_HI", "FL_TOT_ANTHOCYAN"]

POOL = ['PROT', 'FIBE', 'SFAT', 'CHOL', 'ATOC', 'ATOA', 'RET', 'ACAR', 'BCAR', 'CRYP', 'LYCO', 'LZ', 'VB1', 'VB2', 'NIAC', 'VB6', 'FA', 'FF', 'CHL', 'VB12', 'B12A', 'VC', 'VD', 'VK', 'CALC', 'PHOS', 'MAGN', 'IRON', 'ZINC', 'COPP', 'SODI', 'POTA', 'SELE', 'CAFF', 'THEO', 'MOIS', 'M161', 'M181', 'M201', 'M221', 'P182', 'P183', 'P184', 'P204', 'F_CITMLB', 'F_OTHER', 'F_JUICE', 'V_DRKGR', 'V_REDOR_TOMATO', 'V_REDOR_OTHER', 'V_STARCHY_POTATO', 'V_STARCHY_OTHER', 'V_OTHER', 'G_WHOLE', 'G_REFINED', 'PF_MEAT', 'PF_CUREDMEAT', 'PF_POULT', 'PF_SEAFD_HI', 'PF_SEAFD_LOW', 'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 'D_MILK', 'D_YOGURT', 'D_CHEESE', 'OILS', 'SOLID_FATS', 'ADD_SUGARS', 'A_DRINKS', 'FL_APIGEN', 'FL_LUTEOL', 'FL_ISORHAM', 'FL_KAEMF', 'FL_MYRIC', 'FL_QUERCE', 'FL_TOT_ANTHOCYAN', 'FL_TOT_FLAVAN3OL', 'FL_TOT_FLAVANONE', 'FL_TOT_ISOFLAV', 'LEGUMES', 'MARINE_N3', 'NATURAL_SUGR']

def cols(features):
    return [f + "_P1K" for f in features]