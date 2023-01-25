import logging
from datetime import datetime
from typing import List

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dt.data_collection import DataCollection
from dt.forecast import Forecast


class ForecastDisplayV2(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)
        # graphics = graphics

    def display(self, canvas):
        forecast_list: List[Forecast] = self.collection.forecast_list
        # max_temp = max(map(lambda a: a.temp, forecast_list))
        # max(forecast_list, key=Forecast.temp)
        max_temp = max(forecast.temp for forecast in forecast_list)
        min_temp = min(map(lambda a: a.temp, forecast_list))
        temp_delta = max_temp - min_temp
        x_multiplier = (self.config.width - 20) / len(forecast_list)

        graphics.DrawText(canvas, self.font_thumb, 0, 5, self.purple, f'{max_temp:.1f}')
        graphics.DrawLine(canvas, 20, 0, 127, 0, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 19, self.purple,
                               f'{min_temp + 3 * temp_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 15, 127, 15, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 33, self.purple,
                               f'{min_temp + 2 * temp_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 29, 127, 29, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 46, self.purple,
                               f'{min_temp + 1 * temp_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 43, 127, 43, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 60, self.purple, f'{min_temp:.1f}')
        graphics.DrawLine(canvas, 20, 57, 127, 57, self.grey)

        graphics.DrawLine(canvas, self.config.zs_width, 0, self.config.zs_width, 56, self.grey)
        # for x in range(len(forecast_list) - 1):  # Hver entry er 3 timer
        # if x % 3 == 0:
        self.draw_temp_graph(canvas, forecast_list, min_temp, x_multiplier, temp_delta)

    def draw_temp_graph(self, canvas, forecast_list: [Forecast], min_temp, x_multiplier, temp_delta):
        y_multiplier = (self.config.height - 8) / temp_delta
        # current_hour = int(datetime.today().strftime("%H"))

        for x in range(len(forecast_list) - 1):
            p1 = forecast_list[x]
            p2 = forecast_list[x + 1]
            # hour = int(datetime.strftime(p1.time_start, "%H"))
            x1pos = round(x * x_multiplier) + 20
            y1pos = round(self.config.height - 8 - ((p1.temp - min_temp) * y_multiplier))
            x2pos = round((x + 1) * x_multiplier) + 20
            y2pos = round(self.config.height - 8 - ((p2.temp - min_temp) * y_multiplier))
            #            self.logger.info("line %s,%s - %s,%s", x1pos, y1pos, x2pos, y2pos)
            if (p1.temp + p2.temp) / 2 > 0:
                c = self.red
            else:
                c = self.light_blue
            graphics.DrawLine(canvas, x1pos, y1pos, x2pos, y2pos, c)
