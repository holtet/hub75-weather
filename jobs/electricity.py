import logging

import requests

from config import Config
from dt.price import Price
from dto import *
from dt.electricity_prices import ElectricityPrices
from jobs.Job import AbstractJob


def job_id():
    return 'electricity_job_id'


def interval() -> int:
    return 3600


class ElectricityFetcher(AbstractJob):

    def __init__(self, collection: DataCollection):
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def run(self):
        datestr = datetime.datetime.today().strftime("%Y/%m-%d")
        url = f'https://www.hvakosterstrommen.no/api/v1/prices/{datestr}_NO1.json'
        self.logger.info("Fetching current electricity prices")
        electricity_prices: ElectricityPrices = ElectricityPrices()
        # 2023-01-06T00:00:00+01:00
        # datetime_format = "%Y-%m%dT%H%M%S"
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
                # reduce(self.compare_max_price(), electricity_prices.prices).price_nok
                electricity_prices.min_price = min(map(lambda x: x.price_nok, electricity_prices.prices))
                # reduce(self.compare_min_price(), electricity_prices.prices).price_nok
                # self.logger.info("Min: %s ", electricity_prices.min_price)
                # self.logger.info("Max: %s ", electricity_prices.max_price)

                # self.logger.info("Min: %s ", min(map(lambda x: x.price_nok, electricity_prices.prices)))
                # self.logger.info("Max: %s ", max(map(lambda x: x.price_nok, electricity_prices.prices)))
                # main = response['main']
                # electricity_prices.temperature = str(round(float(main['temp']) - 273.15, 1))
                # electricity_prices.humidity = self.to_float_str(main['humidity'])
                # if 'sea_level' not in main:
                #     electricity_prices.pressure = self.to_float_str(main['pressure'])
                # else:
                #     electricity_prices.pressure = self.to_float_str(main['sea_level'])
                # weather = response['weather']
                # electricity_prices.icon = weather[0]['icon']
                # electricity_prices.weather_description = weather[0]['description']
                # electricity_prices.city = response['name']
                # electricity_prices.wind_speed = response['wind']['speed']
                # if 'deg' in response['wind']:
                #     electricity_prices.wind_dir = response['wind']['deg']
                # electricity_prices.clouds = response['clouds']['all']
                # if 'rain' in response:
                #     rain = response['rain']
                #     if '1h' in rain:
                #         electricity_prices.rain_1h = float(rain['1h'])
                #     if '3h' in rain:
                #         electricity_prices.rain_3h = float(rain['3h'])
                # if 'snow' in response:
                #     snow = response['snow']
                #     if '1h' in snow:
                #         electricity_prices.snow_1h = float(snow['1h'])
                #     if '3h' in snow:
                #         electricity_prices.snow_3h = float(snow['3h'])
                #
                # electricity_prices.set_header_text()
                # electricity_prices.set_detail_text2()
            else:
                self.logger.error("Current prices not found")
                raise Exception("Current prices not found")
        except Exception as e:
            self.logger.error('Fetching current prices failed: %s', str(e))
            raise
        # self.read_icon(electricity_prices)
        self.collection.electricity_prices = electricity_prices

    # def compare_min_price(self):
    #     return lambda x, y: x if x.price_nok < y.price_nok else y
    #
    # def compare_max_price(self):
    #     return lambda x, y: x if x.price_nok > y.price_nok else y

    # @staticmethod
    # def to_float_str(inputstr):
    #     return str(round(float(inputstr), 1))
    #
    # def read_icon(self, weather_data: CurrentWeatherData):
    #     # print(f'Loading icon {cwd.icon}.bmp')
    #     try:
    #         weather_data.weather_icon = Image.open(f'{weather_data.icon}.bmp').convert('RGB')
    #     except IOError:
    #         self.logger.error('Icon %s not found', {weather_data.icon})
    #         weather_data.weather_icon = Image.open('../unknown.bmp').convert('RGB')
