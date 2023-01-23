import configparser
import logging

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from coordinator import Coordinator
from dt.data_collection import DataCollection
from dt.job import Job
from jobs.current_weather_fetcher import CurrentWeatherFetcher
from jobs.entur_fetcher import TrainDepartureFetcher
from jobs.indoor_environment_fetcher import IndoorEnvironmentFetcher
from jobs.abstract_job import AbstractJob
from jobs.electricity_fetcher import ElectricityFetcher
from jobs.job_exception import JobException
from led_display import LedDisplayThread
from listener import Listener
from jobs.news_fetcher import NewsFetcher
from jobs.weather_forecast_fetcher import WeatherForecastFetcher
import traceback

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.WARNING)


def start_job(job: AbstractJob):
    try:
        job.run()
    except JobException as e:
        print(f'Failed to run job {job.job_id()}. {e.message}')
        traceback.print_exc()

    job_job = scheduler.add_job(job.run,
                                trigger='interval',
                                seconds=job.interval(),
                                id=job.job_id())
    joblist[job.job_id()] = Job(job_job, job.interval(), job.retry_interval())


# Main function
if __name__ == "__main__":
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    config = Config(config_parser)

    dataCollection = DataCollection()

    job_defaults = {
        'coalesce': True
    }

    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    joblist = {}

    start_job(ElectricityFetcher(dataCollection))

    start_job(WeatherForecastFetcher(dataCollection, config))

    tdf = TrainDepartureFetcher(dataCollection, config)
    start_job(tdf)

    current_weather_fetcher = CurrentWeatherFetcher(dataCollection, config)
    start_job(current_weather_fetcher)

    ief = IndoorEnvironmentFetcher(dataCollection)
    start_job(ief)

    news_fetcher = NewsFetcher(dataCollection, config)
    start_job(news_fetcher)

    scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

    Coordinator(dataCollection, config, scheduler).start()

    LedDisplayThread(dataCollection, config).start()
