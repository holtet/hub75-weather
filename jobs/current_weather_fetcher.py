import logging
import requests

from dt.current_weather_data import CurrentWeatherData
from dt.data_collection import DataCollection
from config import Config
from jobs.abstract_job import AbstractJob
from jobs.job_exception import JobException


class CurrentWeatherFetcher(AbstractJob):

    def __init__(self, collection: DataCollection, config: Config):
        self.collection = collection
        self.OWM_str = f'{config.weather_url}{config.weather_city_id}&appid={config.weather_api_key}'
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Fetching current weather")
        new_weather_data = CurrentWeatherData()
        try:
            response = requests.get(self.OWM_str).json()
            if response['cod'] != '404':
                main = response['main']
                new_weather_data.temperature = str(round(float(main['temp']) - 273.15, 1))
                new_weather_data.humidity = self.to_float_str(main['humidity'])
                if 'sea_level' not in main:
                    new_weather_data.pressure = self.to_float_str(main['pressure'])
                else:
                    new_weather_data.pressure = self.to_float_str(main['sea_level'])
                weather = response['weather']
                new_weather_data.icon = weather[0]['icon']
                new_weather_data.weather_description = weather[0]['description']
                new_weather_data.city = response['name']
                new_weather_data.wind_speed = response['wind']['speed']
                if 'deg' in response['wind']:
                    new_weather_data.wind_dir = response['wind']['deg']
                new_weather_data.clouds = response['clouds']['all']
                if 'rain' in response:
                    rain = response['rain']
                    if '1h' in rain:
                        new_weather_data.rain_1h = float(rain['1h'])
                    if '3h' in rain:
                        new_weather_data.rain_3h = float(rain['3h'])
                if 'snow' in response:
                    snow = response['snow']
                    if '1h' in snow:
                        new_weather_data.snow_1h = float(snow['1h'])
                    if '3h' in snow:
                        new_weather_data.snow_3h = float(snow['3h'])

                new_weather_data.set_header_text()
                new_weather_data.set_detail_text2()
            else:
                raise JobException("Current weather not found")
        except Exception as e:
            raise JobException(f'Fetching current weather failed: {str(e)}')
        self.collection.current_weather_data = new_weather_data

    @staticmethod
    def to_float_str(inputstr):
        return str(round(float(inputstr), 1))

    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600

    @staticmethod
    def job_id():
        return 'weather_job_id'
