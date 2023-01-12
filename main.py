import configparser
import logging

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from const import *
from coordinator import Coordinator
from current_weather import CurrentWeatherFetcher
from dto import *
from entur import TrainDepartureFetcher
from indoor_environment import IndoorEnvironmentFetcher
from jobs.Job import AbstractJob
from jobs.electricity import ElectricityFetcher
from led_display import LedDisplayThread
from listener import Listener
from news import NewsFetcher
from weather_forecast import WeatherForecastFetcher

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.INFO)

# Main function
if __name__ == "__main__":
    configp = configparser.ConfigParser()
    configp.read('config.ini')
    config = Config(configp)

    dataCollection = DataCollection()

    job_defaults = {
        'coalesce': True
    }

    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    joblist = {}

    electricity: AbstractJob = ElectricityFetcher(dataCollection)
    electricity.run()
    electricity_job = scheduler.add_job(electricity.run,
                                        trigger='interval',
                                        seconds=electricity.interval(),
                                        id=electricity.job_id())
    joblist[electricity.job_id()] = Job(electricity_job, electricity.interval(), 600)
    # Lag metode for start+add jobb

    wff = WeatherForecastFetcher(dataCollection, config)
    wff.run()
    wff_job = scheduler.add_job(wff.run, trigger='interval', seconds=3600, id=WFF_JOB_ID)
    joblist[WFF_JOB_ID] = Job(wff_job, 3600, 600)

    tdf = TrainDepartureFetcher(dataCollection, config)
    tdf.run()
    tdf_job = scheduler.add_job(tdf.run, trigger='interval', seconds=300, id=TDF_JOB_ID)
    joblist[TDF_JOB_ID] = Job(tdf_job, 300, 150)

    cwf = CurrentWeatherFetcher(dataCollection, config)
    cwf.run()
    cwf_job = scheduler.add_job(cwf.run, trigger='interval', seconds=3600, id=CWF_JOB_ID)
    joblist[CWF_JOB_ID] = Job(cwf_job, 3600, 600)

    ief = IndoorEnvironmentFetcher(dataCollection)
    ief.run()
    ief_job = scheduler.add_job(ief.run, trigger='interval', seconds=2, id=IEF_JOB_ID)
    joblist[IEF_JOB_ID] = Job(ief_job, 2, 2)

    nf = NewsFetcher(dataCollection, config)
    try:
        nf.run()
    except Exception as e:
        print("Failed to fetch news")
    nf_job = scheduler.add_job(nf.run, trigger='interval', seconds=3600, id=NF_JOB_ID)
    joblist[NF_JOB_ID] = Job(nf_job, 3600, 600)

    scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

    #    stopFlag = Event()

    cthread = Coordinator(dataCollection, config, scheduler)
    cthread.start()

    lthread = LedDisplayThread(dataCollection, config)
    lthread.start()
