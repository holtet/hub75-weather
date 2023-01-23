import logging

from display.ElectricityDisplay import ElectricityDisplay
from dt.data_collection import DataCollection
# from dto import *
# from dt.electricity_prices import ElectricityPrices
from config import Config
from jobs.electricity import ElectricityFetcher
import configparser

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s %(message)s', level=logging.INFO)


# Main function
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    configp = configparser.ConfigParser()
    configp.read('config-test.ini')
    config = Config(configp)

    dataCollection = DataCollection()

    # job_defaults = {
    #     'coalesce': True
    # }
    #
    # scheduler = BackgroundScheduler(job_defaults=job_defaults)
    # joblist = {}

    electricity_fetcher = ElectricityFetcher(dataCollection)
    electricity_fetcher.run()
    electricity_prices = dataCollection.electricity_prices
    logger.info("Min: %s ", electricity_prices.min_price)
    logger.info("Max: %s ", electricity_prices.max_price)
    logger.info("Size: %s ", len(electricity_prices.prices))
    ts = electricity_prices.prices[0].time_start
    datetime_format = "%Y-%m%dT%H%M%S"
    print(f'S: {electricity_fetcher.interval()}')
    print(f'J: {electricity_fetcher.job_id()}')

    for p in electricity_prices.prices:
        # logger.info("\n%s, %s", p.time_start)
        logger.info("\n%s, %s", p.price_nok, datetime.datetime.strftime(p.time_start, "%H"))
    # logger.info("Date: %s \n%s", ts, datetime.datetime.fromisoformat(ts))
    eld = ElectricityDisplay(config)
    eld.display(electricity_prices, offscreen_canvas)

#     wff_job = scheduler.add_job(wff.run, trigger='interval', seconds=3600, id=WFF_JOB_ID)
#     joblist[WFF_JOB_ID] = Job(wff_job, 3600, 600)
#
#     tdf = TrainDepartureFetcher(dataCollection, config)
#     tdf.run()
#     tdf_job = scheduler.add_job(tdf.run, trigger='interval', seconds=300, id=TDF_JOB_ID)
#     joblist[TDF_JOB_ID] = Job(tdf_job, 300, 150)
#
#     cwf = CurrentWeatherFetcher(dataCollection, config)
#     cwf.run()
#     cwf_job = scheduler.add_job(cwf.run, trigger='interval', seconds=3600, id=CWF_JOB_ID)
#     joblist[CWF_JOB_ID] = Job(cwf_job, 3600, 600)
#
#     ief = IndoorEnvironmentFetcher(dataCollection)
#     ief.run()
#     ief_job = scheduler.add_job(ief.run, trigger='interval', seconds=2, id=IEF_JOB_ID)
#     joblist[IEF_JOB_ID] = Job(ief_job, 2, 2)
#
#     nf = NewsFetcher(dataCollection, config)
#     try:
#         nf.run()
#     except Exception as e:
#         print("Failed to fetch news")
#     nf_job = scheduler.add_job(nf.run, trigger='interval', seconds=3600, id=NF_JOB_ID)
#     joblist[NF_JOB_ID] = Job(nf_job, 3600, 600)
#
#     scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#
#     scheduler.start()
#
# #    stopFlag = Event()
#
#     cthread = Coordinator(dataCollection, config, scheduler)
#     cthread.start()
#
#     lthread = LedDisplayThread(dataCollection, config)
#     lthread.start()
