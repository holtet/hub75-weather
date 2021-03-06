import logging
import requests
from datetime import datetime
from dto import *
from config import Config


class WeatherForecastFetcher:

    def __init__(self, collection: DataCollection, config1: Config):
        self.collection = collection
        self.OWM_str = f'http://api.openweathermap.org/data/2.5/forecast?id={config1.city_id}&appid={config1.api_key}'
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            self.logger.info("Fetching weather forecast")
            response = requests.get(self.OWM_str).json()
            # print(response.content)
            # response2 = response.json()
            if response['cod'] != '404':
                self.collection.forecast_list = []
                forecasts = response['list']
                for forecast in forecasts:
                    fore = Forecast()
                    dt = datetime.datetime.fromtimestamp(forecast['dt'])
                    fore.weekday = dt.strftime('%a %d/%m')
                    fore.timestr = dt.strftime('%H:%M')
                    main = forecast['main']
                    fore.temp = str(round(float(main['temp']) - 273.15, 1))
                    fore.weather_desc = forecast['weather'][0]['description']
                    fore.wind_speed = forecast['wind']['speed']
                    fore.clouds = forecast['clouds']['all']
                    if 'rain' in forecast and '3h' in forecast['rain']:
                        fore.rain_3h = float(forecast['rain']['3h'])
                    if 'snow' in forecast and '3h' in forecast['snow']:
                        fore.snow_3h = float(forecast['snow']['3h'])
                    fore.set_detail_text()
                    self.collection.forecast_list.append(fore)
            else:
                raise Exception("Weather forecast not found")
        except Exception as e:
            self.logger.error('Weather forecast fetcher failed: %s', str(e))
            raise e
