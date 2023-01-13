import logging
from typing import List

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dto import Departure


class TrainDisplay(Display):

    def __init__(self, config: Config, departures: List[Departure]):
        self.config = config
        self.departures = departures
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        graphics.DrawLine(canvas, 0, 1, self.config.zs_width, 1, self.dark_blue)

        for index, departure in enumerate(self.departures, start=0):
            if departure.delay < 1:
                dep_color = self.green
            elif departure.delay < 8:
                dep_color = self.orange
            else:
                dep_color = self.red

            y0 = index * 6 + 2
            y1 = y0 + 5
            graphics.DrawText(canvas, self.font_thumb, 0, y1, dep_color, departure.train_name())
            for y in range(y0, y1):
                graphics.DrawLine(canvas, self.config.width - 19, y, self.config.zs_width, y, self.black)
            graphics.DrawLine(canvas, self.config.width - 20, y0, self.config.width - 20, y1, self.dark_blue)
            graphics.DrawLine(canvas, 0, y1, self.config.zs_width, y1, self.dark_blue)
            graphics.DrawText(canvas, self.font_thumb, self.config.width - 19, y1, dep_color,
                              departure.departure_time())
