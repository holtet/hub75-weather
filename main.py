import logging
import bme280
import smbus2
import time
import datetime
from os import wait
from threading import Thread, Event
#import requests
#import json
#import aiohttp
#import asyncio
#from enturclient import EnturPublicTransportData
#from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
#from PIL import Image
#from apds9960.const import *
#from apds9960 import APDS9960
from dto import *
from coordinator import Coordinator
from entur import TrainDepartureFetcher
from current_weather import CurrentWeatherFetcher
from weather_forecast import WeatherForecastFetcher
from indoor_environment import IndoorEnvironmentFetcher
from led_display import LedDisplayThread
from const import *
import configparser
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.WARNING)


class Listener:
    def __init__(self, joblist1):
        self.joblist = joblist1
        self.logger = logging.getLogger("Listener") # __name__

    def job_done_listener(self, event):
        job = joblist[event.job_id]
        if event.exception:
            self.logger.info('The job %s crashed', {event.job_id})
            if job.last_success:
                job.job.reschedule(trigger='interval', seconds=job.interval_error)
                job.last_success = False
        else:
            self.logger.info('The job %s was successful', {event.job_id})
            if not job.last_success:
                job.job.reschedule(trigger='interval', seconds=job.interval_ok)
                job.last_success = True


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

    scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

    stopFlag = Event()

#    thread3 = IndoorEnvironmentFetcherThread(stopFlag, dataCollection)
#    thread3.start()

    thread4 = Coordinator(stopFlag, dataCollection, config, scheduler)
    thread4.start()

    run_text = LedDisplayThread(stopFlag, dataCollection)
    run_text.start()
