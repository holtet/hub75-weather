import logging
from datetime import datetime

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dt.electricity_prices import ElectricityPrices


class ElectricityDisplay(Display):
#    logger = logging.getLogger(__name__)

    def __init__(self, config: Config, electricity_prices: ElectricityPrices):
        self.config = config
        self.electricity_prices = electricity_prices
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        y_multiplier = (self.config.height-8) / (self.electricity_prices.max_price - self.electricity_prices.min_price)
        x_multiplier = (self.config.width-20) / len(self.electricity_prices.prices)

        current_hour = int(datetime.today().strftime("%H"))
        current_minute = datetime.today().strftime("%M")

        graphics.DrawText(canvas, self.font_thumb, 0, 5, self.purple, f'{self.electricity_prices.max_price:.1f}')
        graphics.DrawText(canvas, self.font_thumb, 0, 63-5, self.purple, f'{self.electricity_prices.min_price:.1f}')
        
        for x in range(len(self.electricity_prices.prices) - 1):

            p1 = self.electricity_prices.prices[x]
            p2 = self.electricity_prices.prices[x + 1]
            hour = int(datetime.strftime(p1.time_start, "%H"))
            x1pos = round(x * x_multiplier)+20
            y1pos = round(self.config.height - 8 - ((p1.price_nok - self.electricity_prices.min_price) * y_multiplier))
            x2pos = round((x + 1) * x_multiplier)+20
            y2pos = round(self.config.height - 8 - ((p2.price_nok - self.electricity_prices.min_price) * y_multiplier))
#            self.logger.info("line %s,%s - %s,%s", x1pos, y1pos, x2pos, y2pos)

            if x % 3 == 0:
 #               self.logger.info("text at %s,%s %s", x1pos, self.config.zs_height - 1, hour)
                graphics.DrawLine(canvas, x1pos, 0, x1pos, 56, self.grey)
            graphics.DrawLine(canvas, x1pos, y1pos, x2pos, y2pos, self.dark_blue)

            if hour == current_hour:
 #               self.logger.info("circle %s,%s", x1pos, y1pos)
                graphics.DrawCircle(canvas, x1pos, y1pos, 2, self.white)

                text = str(round(float(p1.price_nok), 1))

                x1textpos = x1pos
                if self.config.width - x1textpos < 12:
                    x1textpos = self.config.width - 12
                if x1textpos < 20:
                    x1textpos = 20 # Skal vel ikke skje

                if y1pos > self.config.height / 2:
                    self.logger.info("text above at %s,%s %s", x1textpos, 10, text)
                    graphics.DrawText(canvas, self.font_thumb, x1textpos, 10, self.purple, f'{text}')
                else:
                    self.logger.info("text below at %s,%s %s", x1textpos, 50, text)
                    graphics.DrawText(canvas, self.font_thumb, x1textpos, 50, self.purple, f'{text}')

            # self.logger.info("%s mod 3 = %s, type of currenthour %s, %s", x, x % 3, type(current_hour), type(x))

            if x % 3 == 0:
 #               self.logger.info("text at %s,%s %s", x1pos, self.config.zs_height - 1, hour)
                graphics.DrawText(canvas, self.font_thumb, x1pos, self.config.zs_height - 0, self.purple, f'{hour}')
        # for p in electricity_prices.prices:
        #     self.logger.info("\n%s, %s", p.price_nok, datetime.strftime(p.time_start, "%H"))
