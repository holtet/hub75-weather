from typing import List

from dt.price import Price


class ElectricityPrices:
    prices: List[Price]

    def __init__(self):
        self.prices = []
