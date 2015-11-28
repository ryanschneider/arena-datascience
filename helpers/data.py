import pandas as pd
import numpy as np
import json


player_classes = ["Warrior", "Shaman", "Rogue", "Paladin", "Hunter", "Druid", "Warlock", "Mage", "Priest"]


def _get_tier_data():
    # zoinks the data from Arena Helper
    raw_tier = pd.read_json("https://raw.githubusercontent.com/rembound/Arena-Helper/master/data/cardtier.json")
    #index is the card id, name is card name, value is a list
    # value is [Warrior, Shaman, Rogue, Paladin, Hunter, Druid, Warlock, Mage, Priest]
    # new columns are CLASS_Tier, CLASS_Tier_DropOff
    extracts = dict()

    for cls in player_classes:
        extracts["{}_Tier".format(cls)] = list()
        extracts["{}_Tier_DropOff".format(cls)] = list()

    for values in raw_tier["value"].values:
        for cls, value in zip(player_classes, values):
            value = value.strip()
            tier_key = "{}_Tier".format(cls)
            drop_key = "{}_Tier_DropOff".format(cls)
            if not value:
                score = np.nan
                dropoff = np.nan
            else:
                # Unleash the Hounds still has ^^?
                dropoff = value.count("*") or value.count("^")
                if dropoff:
                    score = int(value[:-dropoff])
                else:
                    score = int(value)
            extracts[tier_key].append(score)
            extracts[drop_key].append(dropoff)

    for key in sorted(extracts.keys()):
        raw_tier[key] = np.array(extracts[key])

    raw_tier = raw_tier.set_index("id")
    return raw_tier


def _create_cards_dataframe():
    with open("AllSets.enUS.json", 'r') as fp:
        all = json.load(fp)

    # don't load cards from these sets, they aren't used in Arena
    excluded_sets = ["Hero Skins", "Missions", "System", "Credits", "Debug", "Promotion", "Tavern Brawl", "Reward"]

    arena_sets = [s for s in all.keys() if s not in excluded_sets]

    #since many fields are missing, we first need to build a set of valid columns names
    column_names = set()
    for set_name in arena_sets:
        for card in all[set_name]:
            column_names = column_names.union(set(card.keys()))

    column_names.add("set")
    column_names.add("draft_weight")

    card_values = dict()
    for col in column_names:
        card_values[col] = []

    weighted_set = u'League of Explorers'
    for set_name in arena_sets:
        for card in all[set_name]:
            for col in column_names:
                if col == "set":
                    card_values["set"].append(set_name)
                elif col == "draft_weight":
                    card_values["draft_weight"].append(1.0 if set_name != weighted_set else 1.25)
                else:
                    card_values[col].append(card.get(col, None))

    cards_df = pd.DataFrame(data=card_values)

    # "Free" cards should be "Common"
    free_cards = cards_df[cards_df.rarity == "Free"].index
    cards_df.loc[free_cards, "rarity"] = "Common"

    # TODO: Remove wing 3 and 4 LOE cards
    cards_df = cards_df.set_index("id")

    # drop any non-real cards
    cards_df = cards_df.dropna(subset=["cost"])
    cards_df = cards_df[cards_df.collectible == True]
    return cards_df


def _create_dataframe():
    cards_df = _create_cards_dataframe()
    tier_df = _get_tier_data()
    for col in tier_df.columns:
        if col.split("_")[0] in player_classes:
            cards_df[col] = tier_df[col]

    cards_df.to_json("./merged_df.json")
    df = pd.read_json("./merged_df.json")
    return df


def load_dataframe():
    return pd.read_json("./merged_df.json")


def img_url(x):
    # if x is a DataFrame, we want the index
    if type(x) is pd.DataFrame:
        return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + x.index + ".png"
    elif type(x) is pd.Series:
        return "http://wow.zamimg.com/images/hearthstone/cards/enus/original/" + x.name + ".png"
