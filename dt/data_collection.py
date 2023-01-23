import datetime

from dt.current_weather_data import CurrentWeatherData
from dt.departure import Departure
from dt.electricity_prices import ElectricityPrices
from dt.indoor_environment_data import IndoorEnvironmentData
from dt.news_item import NewsItem


class DataCollection:
    def __init__(self):
        self.brightness = 0
        self.datetime = ""
        self.screen = 0
        self.current_screen_time = 0
        self.indoor_environment_data = IndoorEnvironmentData()
        self.current_weather_data = CurrentWeatherData()
        self.electricity_prices_today = ElectricityPrices()
        self.departure_list = []
        self.news_list = []
        for i in range(0, 8):
            self.departure_list.append(Departure("", datetime.time(0, 0, 0), 0, 128))
            self.news_list.append(NewsItem(""))
        self.ambient_light = 100
        self.forecast_list = []
