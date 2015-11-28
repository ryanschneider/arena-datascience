import random
import pandas as pd
import numpy as np

from helpers.data import load_dataframe


cards_df = load_dataframe()


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

