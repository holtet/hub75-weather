import aiohttp
import asyncio
import logging
from enturclient import EnturPublicTransportData

from config import Config
from dto import *


class TrainDepartureFetcher:

    def __init__(self, collection: DataCollection, config1: Config):
        self.collection = collection
        self.config = config1
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Fetching train departures")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.print_train_delay())
        except Exception as e:
            self.logger.error('Failed to fetch train times: %s', str(e))
            raise e

    async def print_train_delay(self):
        async with aiohttp.ClientSession() as client:
            stop_id = f'NSR:StopPlace:{self.config.stop_id}'
            stops = [stop_id]
            data = EnturPublicTransportData(
                client_name=self.config.entur_client_id,
                stops=stops,
                omit_non_boarding=True,
                number_of_departures=self.config.max_train_departures + 5,
                web_session=client)
            await data.update()

            train = data.get_stop_info(stop_id)
            dindex = 0
            for index, call in enumerate(train.estimated_calls):
                #                print(f'|{call.front_display}|')
                #                for d in self.destinations:
                #                    print(f'destination: |{d}|')
                if dindex < self.config.max_train_departures and call.front_display in self.config.destinations:  # or (1 == 1):
                    old_pos = self.collection.departure_list[dindex].pos
                    departure = Departure(call.front_display, call.aimed_departure_time, call.delay_in_min, old_pos)
                    self.collection.departure_list[dindex] = departure
                    dindex += 1
            #                else:
            #                    print(f'Skipped train departure |{call.front_display}|, dindex {dindex}')
            while dindex < self.config.max_train_departures:
                self.collection.departure_list[dindex] = Departure("", "", 0, 0)
                dindex += 1
