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
                for forecast_json in forecasts:
                    forecast = Forecast()
                    dt = datetime.fromtimestamp(forecast_json['dt'])
                    forecast.weekday = dt.strftime('%a %d/%m')
                    forecast.time = dt.strftime('%H:%M')
                    main = forecast_json['main']
                    forecast.temp = str(round(float(main['temp']) - 273.15, 1))
                    forecast.weather_desc = forecast_json['weather'][0]['description']
                    forecast.wind_speed = forecast_json['wind']['speed']
                    forecast.clouds = forecast_json['clouds']['all']
                    if 'rain' in forecast_json and '3h' in forecast_json['rain']:
                        forecast.rain_3h = float(forecast_json['rain']['3h'])
                    if 'snow' in forecast_json and '3h' in forecast_json['snow']:
                        forecast.snow_3h = float(forecast_json['snow']['3h'])
                    forecast.set_detail_text()
                    self.collection.forecast_list.append(forecast)
                self.logger.warning(f'Found a list of {len(self.collection.forecast_list)} forecasts')
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
