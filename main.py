import configparser
import logging

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from coordinator import Coordinator
from jobs.current_weather import CurrentWeatherFetcher
from dto import *
from jobs.entur import TrainDepartureFetcher
from jobs.indoor_environment import IndoorEnvironmentFetcher
from jobs.Job import AbstractJob
from jobs.electricity import ElectricityFetcher
from led_display import LedDisplayThread
from listener import Listener
from jobs.news import NewsFetcher
from jobs.weather_forecast import WeatherForecastFetcher

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.WARNING)


def start_job(job: AbstractJob):
    job.run()
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

    electricity: AbstractJob = ElectricityFetcher(dataCollection)
    start_job(electricity)
    # electricity.run()
    # electricity_job = scheduler.add_job(electricity.run,
    #                                     trigger='interval',
    #                                     seconds=electricity.interval(),
    #                                     id=electricity.job_id())
    # joblist[electricity.job_id()] = Job(electricity_job, electricity.interval(), 600)

    wff = WeatherForecastFetcher(dataCollection, config)
    start_job(wff)
    # wff.run()
    # wff_job = scheduler.add_job(wff.run, trigger='interval', seconds=3600, id=WFF_JOB_ID)
    # joblist[WFF_JOB_ID] = Job(wff_job, 3600, 600)

    tdf = TrainDepartureFetcher(dataCollection, config)
    start_job(tdf)
    # tdf.run()
    # tdf_job = scheduler.add_job(tdf.run, trigger='interval', seconds=300, id=TDF_JOB_ID)
    # joblist[TDF_JOB_ID] = Job(tdf_job, 300, 150)

    current_weather_fetcher = CurrentWeatherFetcher(dataCollection, config)
    start_job(current_weather_fetcher)
    # cwf.run()
    # cwf_job = scheduler.add_job(cwf.run, trigger='interval', seconds=3600, id=CWF_JOB_ID)
    # joblist[CWF_JOB_ID] = Job(cwf_job, 3600, 600)

    ief = IndoorEnvironmentFetcher(dataCollection)
    start_job(ief)
    # ief.run()
    # ief_job = scheduler.add_job(ief.run, trigger='interval', seconds=2, id=IEF_JOB_ID)
    # joblist[IEF_JOB_ID] = Job(ief_job, 2, 2)

    news_fetcher = NewsFetcher(dataCollection, config)
    start_job(news_fetcher)

    # try:
    #     nf.run()
    # except Exception as e:
    #     print("Failed to fetch news")
    # nf_job = scheduler.add_job(nf.run, trigger='interval', seconds=3600, id=NF_JOB_ID)
    # joblist[NF_JOB_ID] = Job(nf_job, 3600, 600)

    scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

    #    stopFlag = Event()

    cthread = Coordinator(dataCollection, config, scheduler)
    cthread.start()

    lthread = LedDisplayThread(dataCollection, config)
    lthread.start()
