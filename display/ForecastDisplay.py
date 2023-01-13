import logging
from typing import List

from rgbmatrix import graphics

from config import Config
from const import SCREEN_FORECAST_3
from display.Display import Display
from dto import NewsItem, DataCollection


class ForecastDisplay(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        offset = 0
        if self.collection.screen == SCREEN_FORECAST_3:
            offset = 4
        # elif self.collection.screen == SCREEN_FORECAST_3:
        #     offset = 8
        # Header
        graphics.DrawLine(canvas, 0, 5, self.config.width - 1, 5, self.dark_blue)
        forecast_0 = self.collection.forecast_list[offset]
        graphics.DrawText(canvas, self.font_thumb, 0, 5, self.purple,
                          f'{self.collection.current_weather_data.city}  {forecast_0.weekday}')

        # + 3 hour
        graphics.DrawText(canvas, self.font_thumb, 0, 11, self.green,
                          f'{forecast_0.time} {forecast_0.temp}C')
        #                graphics.DrawText(canvas, font, 0, 17, green, f'{self.collection.forecast_list[offset].weather_desc}')
        detail_length1 = graphics.DrawText(canvas, self.font_thumb,
                                           forecast_0.detail_text.pos, 17, self.green,
                                           f'{forecast_0.detail_text.text}')
        forecast_0.detail_text.scroll(detail_length1)

        # + 6 hour
        graphics.DrawLine(canvas, 0, 18, self.config.width - 1, 18, self.dark_blue)
        forecast_2 = self.collection.forecast_list[offset + 2]
        graphics.DrawText(canvas, self.font_thumb, 0, 25, self.green,
                          f'{forecast_2.time} {forecast_2.temp}C')
        #                graphics.DrawText(canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
        detail_length2 = graphics.DrawText(canvas, self.font_thumb,
                                           forecast_2.detail_text.pos, 31,
                                           self.green,
                                           f'{forecast_2.detail_text.text}')
        forecast_2.detail_text.scroll(detail_length2)

        # + 9 hour
        graphics.DrawLine(canvas, 0, 32, self.config.width - 1, 32, self.dark_blue)
        forecast_4 = self.collection.forecast_list[offset + 4]
        graphics.DrawText(canvas, self.font_thumb, 0, 39, self.green,
                          f'{forecast_4.time} {forecast_4.temp}C')
        #                graphics.DrawText(canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
        detail_length3 = graphics.DrawText(canvas, self.font_thumb,
                                           forecast_4.detail_text.pos, 45,
                                           self.green,
                                           f'{forecast_4.detail_text.text}')
        forecast_4.detail_text.scroll(detail_length3)

        # + 12 hour
        graphics.DrawLine(canvas, 0, 46, self.config.width - 1, 46, self.dark_blue)
        forecast_6 = self.collection.forecast_list[offset + 6]
        graphics.DrawText(canvas, self.font_thumb, 0, 53, self.green,
                          f'{forecast_6.time} {forecast_6.temp}C')
        #                graphics.DrawText(canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
        detail_length4 = graphics.DrawText(canvas, self.font_thumb,
                                           forecast_6.detail_text.pos, 59,
                                           self.green,
                                           f'{forecast_6.detail_text.text}')
        forecast_6.detail_text.scroll(detail_length4)

