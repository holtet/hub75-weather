import logging
import requests
from datetime import datetime

from config import Config
from dt.data_collection import DataCollection
from dt.forecast import Forecast
from jobs.abstract_job import AbstractJob
from jobs.job_exception import JobException


class WeatherForecastFetcher(AbstractJob):

    def __init__(self, collection: DataCollection, config: Config):
        self.collection = collection
        self.OWM_str = f'{config.forecast_url}{config.weather_city_id}&appid={config.weather_api_key}'
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            self.logger.info("Fetching weather forecast")
            response = requests.get(self.OWM_str).json()
            if response['cod'] != '404':
                self.collection.forecast_list = []
                forecasts = response['list']
                for forecast in forecasts:
                    fore = Forecast()
                    dt = datetime.fromtimestamp(forecast['dt'])
                    fore.weekday = dt.strftime('%a %d/%m')
                    fore.time = dt.strftime('%H:%M')
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
                raise JobException("Weather forecast not found")
        except Exception as e:
            raise JobException(f'Weather forecast fetcher failed: {repr(e)}')

    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600

    @staticmethod
    def job_id():
        return 'forecast_job_id'
