import logging
from datetime import datetime, timedelta

import requests

from dt.data_collection import DataCollection
from dt.electricity_prices import ElectricityPrices
from dt.price import Price
from jobs.abstract_job import AbstractJob


class ElectricityFetcher(AbstractJob):

    def __init__(self, collection: DataCollection):
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def run(self):
        datestring_today = datetime.today().strftime("%Y/%m-%d")
        datestring_tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y/%m-%d")
        # url_tomorrow = f'https://www.hvakosterstrommen.no/api/v1/prices/{datestring_tomorrow}_NO1.json'

        electricity_prices: ElectricityPrices = ElectricityPrices()

        electricity_prices.prices_today = self.create_price_list(datestring_today)
        electricity_prices.prices_tomorrow = self.create_price_list(datestring_tomorrow)
        electricity_prices.prices.extend(electricity_prices.prices_today)
        electricity_prices.prices.extend(electricity_prices.prices_tomorrow)

        electricity_prices.max_price = max(map(lambda x: x.price_nok, electricity_prices.prices))
        electricity_prices.min_price = min(map(lambda x: x.price_nok, electricity_prices.prices))

    def create_price_list(self, datestring):
        url_today = f'https://www.hvakosterstrommen.no/api/v1/prices/{datestring}_NO1.json'
        self.logger.warning(f'Fetching current electricity prices for {datestring}')
        # electricity_prices: ElectricityPrices = ElectricityPrices()
        prices: [Price] = []
        try:
            response = requests.get(url_today)
            if response.status_code == 200:
                json = response.json()
                for value in json:
                    price = Price()
                    price.price_nok = value['NOK_per_kWh'] * 1.25
                    price.time_start = datetime.fromisoformat(value['time_start'])
                    prices.append(price)
                    # electricity_prices.prices.append(price)
            else:
                self.logger.error("Current prices not found")
                raise Exception("Current prices not found")
        except Exception as e:
            self.logger.error('Fetching current prices failed: %s', str(e))
            raise
        return prices

    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600

    @staticmethod
    def job_id():
        return 'electricity_job_id'
