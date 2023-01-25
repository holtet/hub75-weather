import logging
from display.ForecastDisplayV2 import ForecastDisplayV2
from dt.data_collection import DataCollection
from config import Config
import configparser

from jobs.weather_forecast_fetcher import WeatherForecastFetcher
from mock_display import MockDisplay, MockCanvas

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.INFO)

# Main function
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    configp = configparser.ConfigParser()
    configp.read('config-test.ini')
    config = Config(configp)

    dataCollection = DataCollection()

    electricity_fetcher = WeatherForecastFetcher(dataCollection)
    electricity_fetcher.run()
    electricity_prices = dataCollection.forecast_list
    # logger.info("Min: %s ", electricity_prices.min_price)
    # logger.info("Max: %s ", electricity_prices.max_price)
    # logger.info("Size: %s ", len(electricity_prices.prices))
    # ts = electricity_prices.prices[0].time_start
    # datetime_format = "%Y-%m%dT%H%M%S"
    # print(f'S: {electricity_fetcher.interval()}')
    # print(f'J: {electricity_fetcher.job_id()}')

    # for p in electricity_prices.prices:
    #     # logger.info("\n%s, %s", p.time_start)
    #     logger.info("\n%s, %s", p.price_nok, datetime.strftime(p.time_start, "%H"))
    # logger.info("Date: %s \n%s", ts, datetime.datetime.fromisoformat(ts))
    # electricity_display = ElectricityDisplay(config, dataCollection)
    # electricity_display.display(MockDisplay())
    fd = ForecastDisplayV2(config, dataCollection)
    fd.display(MockCanvas())
