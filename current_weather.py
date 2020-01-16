import requests
from dto import *
from PIL import Image

class CurrentWeatherFetcher:

    def __init__(self, collection: DataCollection, config1: Config):
        self.collection = collection
        self.OWM_str = f'http://api.openweathermap.org/data/2.5/weather?id={config1.city_id}&appid={config1.api_key}'
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        self.logger.info("Fetching current weather")
        new_weather_data = CurrentWeatherData()
        try:
            x = requests.get(self.OWM_str).json()
            if x['cod'] != '404':
                y = x['main']
                new_weather_data.temperature = str(round(float(y['temp']) - 273.15, 1))
                new_weather_data.humidity = self.to_float_str(y['humidity'])
                if 'sea_level' not in y:
                    new_weather_data.pressure = self.to_float_str(y['pressure'])
                else:
                    new_weather_data.pressure = self.to_float_str(y['sea_level'])
                z = x['weather']
                new_weather_data.icon = z[0]['icon']
                new_weather_data.weather_description = z[0]['description']
                new_weather_data.city = x['name']
                new_weather_data.wind_speed = x['wind']['speed']
                if 'deg' in x['wind']:
                    new_weather_data.wind_dir = x['wind']['deg']
                new_weather_data.clouds = x['clouds']['all']
                if 'rain' in x:
                    rain = x['rain']
                    if '1h' in rain:
                        new_weather_data.rain_1h = float(rain['1h'])
                    if '3h' in rain:
                        new_weather_data.rain_3h = float(rain['3h'])
                if 'snow' in x:
                    snow = x['snow']
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
            raise e
        self.read_icon(new_weather_data)
        self.collection.current_weather_data = new_weather_data

    def to_float_str(self, inputstr):
        return str(round(float(inputstr), 1))

    def read_icon(self, cwd: CurrentWeatherData):
    # print(f'Loading icon {cwd.icon}.bmp')
        try:
            cwd.weather_icon = Image.open(f'{cwd.icon}.bmp').convert('RGB')
        except:
            self.logger.error('Icon %s not found', {cwd.icon})
            cwd.weather_icon = Image.open('unknown.bmp').convert('RGB')
