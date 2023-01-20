import logging

import requests

from dt.price import Price
from dto import *
from jobs.Job import AbstractJob


class ElectricityFetcher(AbstractJob):

    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600

    @staticmethod
    def job_id():
        return 'electricity_job_id'

    def __init__(self, collection: DataCollection):
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def run(self):
        datestr = datetime.datetime.today().strftime("%Y/%m-%d")
        url = f'https://www.hvakosterstrommen.no/api/v1/prices/{datestr}_NO1.json'
        self.logger.warning(f'Fetching current electricity prices for {datestr}')
        electricity_prices: ElectricityPrices = ElectricityPrices()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                json = response.json()
                for value in json:
                    price = Price()
                    price.price_nok = value['NOK_per_kWh']
                    price.time_start = datetime.datetime.fromisoformat(value['time_start'])
                    electricity_prices.prices.append(price)
                electricity_prices.max_price = max(map(lambda x: x.price_nok, electricity_prices.prices))
                electricity_prices.min_price = min(map(lambda x: x.price_nok, electricity_prices.prices))
            else:
                self.logger.error("Current prices not found")
                raise Exception("Current prices not found")
        except Exception as e:
            self.logger.error('Fetching current prices failed: %s', str(e))
            raise
        self.collection.electricity_prices = electricity_prices
