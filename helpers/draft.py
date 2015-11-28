import random
import json

import pandas as pd
import numpy as np


class WeightedRandomizer:
    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append ( (self.__max, value) )

    def random (self):
        r = random.random () * self.__max
        for ceil, value in self.__weights:
            if ceil > r:
                return value

player_classes = [u'Mage', u'Paladin', u'Warlock', u'Warrior', u'Hunter', u'Priest', u'Shaman', u'Druid', u'Rogue']
w = {"Legendary": 0.75, "Epic": 3.76, "Rare": 16.9, "Common": 78.59}
wr = WeightedRandomizer(w)


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
    cards_df[cards_df.rarity == "Free"] = "Common"

    # TODO: Remove wing 3 and 4 LOE cards
    cards_df = cards_df.set_index("id")

    # drop any non-real cards
    cards_df = cards_df.dropna(subset=["cost"])
    cards_df = cards_df[cards_df.collectible == True]
    return cards_df


def _create_draft_lists(cards_df):
    rarities = cards_df.rarity.unique()
    draftables = dict()

    for c in player_classes:
        # Class cards get a 100% weight bump
        class_cards = cards_df[cards_df.playerClass == c].copy()
        class_cards.draft_weight += 1

        # and then add the neutral cards
        class_cards = class_cards.append(cards_df[cards_df.playerClass.isnull()])
        cards_by_rarity = dict()
        for rarity in rarities:
            cards_by_rarity[rarity] = class_cards[class_cards.rarity == rarity]
        draftables[c] = cards_by_rarity

    return draftables


cards_df = _create_cards_dataframe()
draftables = _create_draft_lists(cards_df)

random_state = np.random.RandomState()


def pick_rarities():
    # picks 1, 15, and 30 are always Rare
    return [wr.random() if i not in [0, 14, 29] else "Rare" for i in range(30)]


def draft_options(playerClass):
    rarities = pick_rarities()
    picks = []

    for rarity in rarities:
        possible = draftables[playerClass][rarity]
        picks.append(possible.sample(weights="draft_weight", n=3, random_state=random_state))
    return picks

