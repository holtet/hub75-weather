import logging
from typing import List

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dt.data_collection import DataCollection
from dt.departure import Departure


class TrainDisplayV2(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        graphics.DrawLine(canvas, 0, 0, self.config.zs_width, 0, self.dark_blue)

        for index, departure in enumerate(self.collection.departure_list, start=0):
            if departure.delay < 1:
                departure_color = self.green
            elif departure.delay < 8:
                departure_color = self.orange
            else:
                departure_color = self.red

            y0 = index * 7 + 1
            y1 = y0 + 5
            graphics.DrawText(canvas, self.font_4x6, 0, y1, departure_color, departure.train_name())
            for y in range(y0, y1):
                graphics.DrawLine(canvas, self.config.width - 19, y, self.config.zs_width, y, self.black)
            graphics.DrawLine(canvas, self.config.width - 20, y0, self.config.width - 20, y1, self.dark_blue)
            graphics.DrawLine(canvas, 0, y1, self.config.zs_width, y1, self.dark_blue)
            graphics.DrawText(canvas, self.font_4x6, self.config.width - 19, y1, departure_color,
                              departure.departure_time())
