import time

import logging
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from threading import Thread

from config import Config
from display.ElectricityDisplay import ElectricityDisplay
from display.ForecastDisplay import ForecastDisplay
from display.IndoorDisplay import IndoorDisplay
from display.NewsDisplay import NewsDisplay
from display.TrainDisplay import TrainDisplay
from dto import *


class LedDisplayThread(Thread):
    def __init__(self, collection: DataCollection, config: Config):
        Thread.__init__(self)
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting display thread")
        height = 64
        width = 128
        options = RGBMatrixOptions()
        options.rows = height
        options.cols = width
        options.row_address_type = 3
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
        options.gpio_slowdown = 1
        options.pwm_lsb_nanoseconds = 60
        options.pwm_bits = 11
        matrix = RGBMatrix(options=options)

        offscreen_canvas = matrix.CreateFrameCanvas()

        electricity_display = ElectricityDisplay(self.config, self.collection)
        indoor_display = IndoorDisplay(self.config, self.collection)
        train_display = TrainDisplay(self.config, self.collection)
        news_display = NewsDisplay(self.config, self.collection)
        forecast_display = ForecastDisplay(self.config, self.collection)

        while True:
            try:
                offscreen_canvas.Clear()
                offscreen_canvas.brightness = \
                    self.collection.brightness * min(self.collection.ambient_light * 2 + 10, 100)

                if self.collection.screen == SCREEN_TRAINS:
                    train_display.display(offscreen_canvas)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_INDOOR:
                    indoor_display.display(offscreen_canvas)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_OUTDOOR:
                    electricity_display.display(offscreen_canvas)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif (
                        self.collection.screen == SCREEN_FORECAST_1
                        or self.collection.screen == SCREEN_FORECAST_2
                        or self.collection.screen == SCREEN_FORECAST_3):
                    forecast_display.display(offscreen_canvas)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_NEWS:
                    news_display.display(offscreen_canvas)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)
            except Exception as e:
                self.logger.error('Failed to show display: %s', str(e))
                time.sleep(3)
