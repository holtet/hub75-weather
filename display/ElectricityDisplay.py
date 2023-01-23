import logging
from datetime import datetime

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dt.electricity_prices import ElectricityPrices
from dt.data_collection import DataCollection
from dt.price import Price


class ElectricityDisplay(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        electricity_prices = self.collection.electricity_prices_today
        price_delta = electricity_prices.max_price - electricity_prices.min_price
        x_multiplier = (self.config.width - 20) / len(electricity_prices.prices_today)

        current_minute = datetime.today().strftime("%M")

        graphics.DrawText(canvas, self.font_thumb, 0, 5, self.purple, f'{electricity_prices.max_price:.1f}')
        graphics.DrawLine(canvas, 20, 0, 127, 0, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 19, self.purple,
                          f'{electricity_prices.min_price + 3 * price_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 15, 127, 15, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 33, self.purple,
                          f'{electricity_prices.min_price + 2 * price_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 29, 127, 29, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 46, self.purple,
                          f'{electricity_prices.min_price + 1 * price_delta / 4:.1f}')
        graphics.DrawLine(canvas, 20, 43, 127, 43, self.grey)
        graphics.DrawText(canvas, self.font_thumb, 0, 60, self.purple, f'{electricity_prices.min_price:.1f}')
        graphics.DrawLine(canvas, 20, 57, 127, 57, self.grey)

        graphics.DrawLine(canvas, self.config.zs_width, 0, self.config.zs_width, 56, self.grey)

        for x in range(len(electricity_prices.prices_today) - 1):
            if x % 3 == 0:
                p1 = electricity_prices.prices[x]
                hour = int(datetime.strftime(p1.time_start, "%H"))
                x1pos = round(x * x_multiplier) + 20
                #               self.logger.info("text at %s,%s %s", x1pos, self.config.zs_height - 1, hour)
                graphics.DrawLine(canvas, x1pos, 0, x1pos, 56, self.grey)
                # if x % 3 == 0:
                #               self.logger.info("text at %s,%s %s", x1pos, self.config.zs_height - 1, hour)
                graphics.DrawText(canvas, self.font_thumb, x1pos, self.config.zs_height - 0, self.purple, f'{hour}')

        self.draw_price_graph(canvas, electricity_prices.prices_today, electricity_prices.min_price,
                              x_multiplier, price_delta, 1, self.light_blue)
        self.draw_price_graph(canvas, electricity_prices.prices_tomorrow, electricity_prices.min_price,
                              x_multiplier, price_delta, 1, self.dark_blue)

        # for p in electricity_prices.prices:
        #     self.logger.info("\n%s, %s", p.price_nok, datetime.strftime(p.time_start, "%H"))

    def draw_price_graph(self, canvas, electricity_prices: [Price], min_price, x_multiplier, price_delta,
                         indicate_current, color):
        y_multiplier = (self.config.height - 8) / price_delta
        current_hour = int(datetime.today().strftime("%H"))

        for x in range(len(electricity_prices) - 1):
            p1 = electricity_prices.prices[x]
            p2 = electricity_prices.prices[x + 1]
            hour = int(datetime.strftime(p1.time_start, "%H"))
            x1pos = round(x * x_multiplier) + 20
            y1pos = round(self.config.height - 8 - ((p1.price_nok - min_price) * y_multiplier))
            x2pos = round((x + 1) * x_multiplier) + 20
            y2pos = round(self.config.height - 8 - ((p2.price_nok - min_price) * y_multiplier))
            #            self.logger.info("line %s,%s - %s,%s", x1pos, y1pos, x2pos, y2pos)
            graphics.DrawLine(canvas, x1pos, y1pos, x2pos, y2pos, color)

            if hour == current_hour and indicate_current:  # Sjekk dagens dato istedet?
                #               self.logger.info("circle %s,%s", x1pos, y1pos)
                x1circlepos = x1pos
                if self.config.width - x1circlepos < 3:
                    x1circlepos = self.config.width - 3
                graphics.DrawCircle(canvas, x1circlepos, y1pos, 2, self.white)

                current_price = str(round(float(p1.price_nok), 1))

                x1textpos = x1pos + 0  # Lage noe så den havner i midten av en rute?
                if self.config.width - x1textpos < 12:
                    x1textpos = self.config.width - 12
                # if x1textpos < 20:
                #     x1textpos = 20  # Skal vel ikke skje

                y1textpos = y1pos + 15
                if y1pos > self.config.height / 2:
                    y1textpos = y1pos - 10
                    # self.logger.info("text above at %s,%s %s", x1textpos, y1pos - 15, text)
                    # graphics.DrawText(canvas, self.font_thumb, x1textpos, y1pos - 10, self.purple, f'{text}')
                # else:
                # self.logger.info("text below at %s,%s %s", x1textpos, y1pos + 15, text)
                graphics.DrawText(canvas, self.font_thumb, x1textpos, y1textpos, self.purple, f'{current_price}')

            # self.logger.info("%s mod 3 = %s, type of currenthour %s, %s", x, x % 3, type(current_hour), type(x))
