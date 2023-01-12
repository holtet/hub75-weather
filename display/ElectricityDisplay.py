import logging
from datetime import datetime

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dt.electricity_prices import ElectricityPrices


class ElectricityDisplay(Display):
    logger = logging.getLogger(__name__)

    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def display(self, electricity_prices: ElectricityPrices, canvas):
        y_multiplier = self.config.height / (electricity_prices.max_price - electricity_prices.min_price)
        x_multiplier = self.config.width / len(electricity_prices.prices)

        current_hour = int(datetime.today().strftime("%H"))
        current_minute = datetime.today().strftime("%M")
        for x in range(len(electricity_prices.prices) - 1):
            p1 = electricity_prices.prices[x]
            p2 = electricity_prices.prices[x + 1]
            hour = int(datetime.strftime(p1.time_start, "%H"))
            x1pos = round(x * x_multiplier)
            y1pos = round(self.config.height - ((p1.price_nok - electricity_prices.min_price) * y_multiplier))
            x2pos = round((x + 1) * x_multiplier)
            y2pos = round(self.config.height - ((p2.price_nok - electricity_prices.min_price) * y_multiplier))
            self.logger.info("line %s,%s - %s,%s", x1pos, y1pos, x2pos, y2pos)
            graphics.DrawLine(canvas, 0, 5, self.config.zs_width, 5, self.dark_blue)

            if hour == current_hour:
                self.logger.info("circle %s,%s", x1pos, y1pos)
                graphics.DrawCircle(canvas, x1pos, y1pos, 2, self.dark_blue)

                text = str(round(float(p1.price_nok), 1))

                x1textpos = x1pos
                if self.config.width - x1textpos < 8:
                    x1textpos = self.config.width - 8
                if x1textpos < 8:
                    x1textpos = 8

                if y1pos > self.config.height / 2:
                    self.logger.info("text above at %s,%s %s", x1textpos, y1pos - 8, text)
                else:
                    self.logger.info("text below at %s,%s %s", x1textpos, y1pos, text)

            # self.logger.info("%s mod 3 = %s, type of currenthour %s, %s", x, x % 3, type(current_hour), type(x))

            if x % 3 == 0:
                self.logger.info("text at %s,%s %s", x1pos, self.config.zs_height - 1, hour)

        # for p in electricity_prices.prices:
        #     self.logger.info("\n%s, %s", p.price_nok, datetime.strftime(p.time_start, "%H"))
