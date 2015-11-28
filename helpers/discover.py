import pandas as pd
import numpy as np

if False:
    df[df.race == "Beast"]
    df[df.race == "Beast"].sample(n=3)
    beasts = df[df.race == "Beast"]
    beasts = df[df.race == "Beast"].copy()

def discover(playerClass, df, needs_weights=True):
    # if needs_weights is False, dataframe is already prepped
    if needs_weights:
        df = df.copy()
        df["discover_weight"] = np.nan
        df.loc[df.playerClass == playerClass, "discover_weight"] = 4.0
        df.loc[df.playerClass.isnull(), "discover_weight"] = 1.0
        df = df.dropna(subset=["discover_weight"])
    picks = df.sample(weights="discover_weight", n=3)
    best = df.ix[picks["{}_Tier".format(playerClass)].argmax()]
    return best, picks, df
