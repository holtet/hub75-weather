import logging
import requests
from PIL import Image
from dto import *
from config import Config


class CurrentWeatherFetcher:

    def __init__(self, collection: DataCollection, config: Config):
        self.collection = collection
        self.OWM_str = f'http://api.openweathermap.org/data/2.5/weather?id={config.weather_city_id}&appid={config.weather_api_key}'
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
                self.logger.error("Current weather not found")
                raise Exception("Current weather not found")
        except Exception as e:
            self.logger.error('Fetching current weather failed: %s', str(e))
            raise
        self.read_icon(new_weather_data)
        self.collection.current_weather_data = new_weather_data

    @staticmethod
    def to_float_str(inputstr):
        return str(round(float(inputstr), 1))

    def read_icon(self, weather_data: CurrentWeatherData):
        # print(f'Loading icon {cwd.icon}.bmp')
        try:
            weather_data.weather_icon = Image.open(f'{weather_data.icon}.bmp').convert('RGB')
        except IOError:
            self.logger.error('Icon %s not found', {weather_data.icon})
            weather_data.weather_icon = Image.open('unknown.bmp').convert('RGB')
