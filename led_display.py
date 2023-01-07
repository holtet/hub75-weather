import time

import logging
from PIL import Image
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from threading import Thread

from config import Config
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

        font_thumb = graphics.Font()
        font_thumb.LoadFont("rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

        font_6x12 = graphics.Font()
        font_6x12.LoadFont("rpi-rgb-led-matrix/fonts/6x12.bdf")

        font_5x7 = graphics.Font()
        font_5x7.LoadFont("rpi-rgb-led-matrix/fonts/5x7.bdf")

        font_6x9 = graphics.Font()
        font_6x9.LoadFont("rpi-rgb-led-matrix/fonts/6x9.bdf")

        home_image = Image.open("heart_house_24.bmp").convert('RGB')

        black = graphics.Color(0, 0, 0)
        red = graphics.Color(128, 0, 0)
        purple = graphics.Color(28, 65, 84)
        light_blue = graphics.Color(78, 0, 78)
        dark_blue = graphics.Color(0, 0, 32)
        green = graphics.Color(0, 128, 0)
        orange = graphics.Color(128, 75, 0)

        while True:
            try:
                offscreen_canvas.Clear()
                offscreen_canvas.brightness = \
                    self.collection.brightness * min(self.collection.ambient_light * 2 + 10, 100)

                if self.collection.screen == SCREEN_TRAINS:
                    graphics.DrawLine(offscreen_canvas, 0, 1, self.config.zs_width, 1, dark_blue)

                    for index, departure in enumerate(self.collection.departure_list, start=0):
                        if departure.delay < 1:
                            dep_color = green
                        elif departure.delay < 8:
                            dep_color = orange
                        else:
                            dep_color = red

                        y0 = index * 6 + 2
                        y1 = y0 + 5
                        text_length = graphics.DrawText(offscreen_canvas, font_thumb, 0, y1, dep_color,
                                                        departure.train_name())
                        # text_length = graphics.DrawText(offscreen_canvas, font, news_item.display.pos, y1,
                        # dep_color, news_item.text1()) news_item.display.scroll(text_length)
                        for y in range(y0, y1):
                            graphics.DrawLine(offscreen_canvas, width - 19, y, self.config.zs_width, y, black)
                        graphics.DrawLine(offscreen_canvas, width - 20, y0, width - 20, y1, dark_blue)
                        graphics.DrawLine(offscreen_canvas, 0, y1, self.config.zs_width, y1, dark_blue)
                        graphics.DrawText(offscreen_canvas, font_thumb, width - 19, y1, dep_color,
                                          departure.departure_time())
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_INDOOR:
                    graphics.DrawLine(offscreen_canvas, 0, 5, self.config.zs_width, 5, dark_blue)
                    graphics.DrawLine(offscreen_canvas, 62, 7, 62, 50, dark_blue)
                    graphics.DrawText(offscreen_canvas, font_5x7, 2, 5, light_blue, f'{self.collection.datetime}')
                    indoor = self.collection.indoor_environment_data
                    outdoor = self.collection.current_weather_data
                    temp_text_length = graphics.DrawText(offscreen_canvas, font_6x12, 9, 16, green,
                                                         f'{indoor.temperature:.1f} C')
                    graphics.DrawText(offscreen_canvas, font_6x12, 9, 25, green, f'{indoor.humidity:.1f} %')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 0, 10, 1, green)
                    #                    graphics.DrawText(offscreen_canvas, font2, 1, 32, green, f'{indoor.pressure:.1f} hPa')
                    #                    graphics.DrawText(offscreen_canvas, font, 1, 32, green, outdoor.weather_description)
                    detail2_length = graphics.DrawText(offscreen_canvas, font_thumb, outdoor.detail_text2.pos,
                                                       height - 2, green,
                                                       outdoor.detail_text2.text)
#                    outdoor.detail_text2.scroll(detail2_length)
                    offscreen_canvas.SetImage(home_image, 11, 26)

                    # outdoor = self.collection.current_weather_data
#                    graphics.DrawLine(offscreen_canvas, 0, 5, self.config.zs_width, 5, dark_blue)
#                    graphics.DrawText(offscreen_canvas, font_thumb, 2, 5, red, f'{self.collection.datetime}')
                    #                    header_text_length = graphics.DrawText(offscreen_canvas, font, outdoor.header_text.pos, 5, red,
                    #                                                           outdoor.header_text.text)
                    #                    outdoor.header_text.scroll(header_text_length)
                    temp_text_length = graphics.DrawText(offscreen_canvas, font_6x12, 72, 16, green,
                                                         f'{outdoor.temperature} C')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length + 63, 10, 1, green)
                    graphics.DrawText(offscreen_canvas, font_6x12, 72, 25, green, f'{outdoor.humidity} %')
                    offscreen_canvas.SetImage(outdoor.weather_icon, 80, 27)
                    graphics.DrawText(offscreen_canvas, font_thumb, 68, 50, green, f'{outdoor.weather_description}')

                    #                detail1_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text1.pos, 25, green, outdoor.detail_text1.text)
                    #                outdoor.detail_text1.scroll(detail1_length)
#                    detail2_length = graphics.DrawText(offscreen_canvas, font_thumb, outdoor.detail_text2.pos,
#                                                       self.config.height - 2, green,
#                                                       outdoor.detail_text2.text)
#                    outdoor.detail_text2.scroll(detail2_length)

                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_OUTDOOR:
                    outdoor = self.collection.current_weather_data
                    graphics.DrawLine(offscreen_canvas, 0, 5, self.config.zs_width, 5, dark_blue)
                    graphics.DrawText(offscreen_canvas, font_thumb, 2, 5, red, f'{self.collection.datetime}')
                    #                    header_text_length = graphics.DrawText(offscreen_canvas, font, outdoor.header_text.pos, 5, red,
                    #                                                           outdoor.header_text.text)
                    #                    outdoor.header_text.scroll(header_text_length)
                    temp_text_length = graphics.DrawText(offscreen_canvas, font_6x12, 1, 14, green,
                                                         f'{outdoor.temperature} C')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 8, 8, 1, green)
                    graphics.DrawText(offscreen_canvas, font_6x12, 1, 23, green, f'{outdoor.humidity} %')
                    offscreen_canvas.SetImage(outdoor.weather_icon, 45, 7)

                    #                detail1_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text1.pos, 25, green, outdoor.detail_text1.text)
                    #                outdoor.detail_text1.scroll(detail1_length)
                    detail2_length = graphics.DrawText(offscreen_canvas, font_thumb, outdoor.detail_text2.pos,
                                                       self.config.height - 2, green,
                                                       outdoor.detail_text2.text)
#                    outdoor.detail_text2.scroll(detail2_length)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                #                elif (self.collection.screen in [SCREEN_FORECAST_1, SCREEN_FORECAST_2, SCREEN_FORECAST_3]):
                elif (
                        self.collection.screen == SCREEN_FORECAST_1
                        or self.collection.screen == SCREEN_FORECAST_2
                        or self.collection.screen == SCREEN_FORECAST_3):
                    offset = 0
                    if self.collection.screen == SCREEN_FORECAST_3:
                        offset = 4
                    # elif self.collection.screen == SCREEN_FORECAST_3:
                    #     offset = 8
                    # Header
                    graphics.DrawLine(offscreen_canvas, 0, 5, width - 1, 5, dark_blue)
                    forecast_0 = self.collection.forecast_list[offset]
                    graphics.DrawText(offscreen_canvas, font_thumb, 0, 5, purple,
                                      f'{self.collection.current_weather_data.city}  {forecast_0.weekday}')

                    # + 3 hour
                    graphics.DrawText(offscreen_canvas, font_thumb, 0, 11, green,
                                      f'{forecast_0.time} {forecast_0.temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 17, green, f'{self.collection.forecast_list[offset].weather_desc}')
                    detail_length1 = graphics.DrawText(offscreen_canvas, font_thumb,
                                                       forecast_0.detail_text.pos, 17, green,
                                                       f'{forecast_0.detail_text.text}')
                    forecast_0.detail_text.scroll(detail_length1)

                    # + 6 hour
                    graphics.DrawLine(offscreen_canvas, 0, 18, width - 1, 18, dark_blue)
                    forecast_2 = self.collection.forecast_list[offset + 2]
                    graphics.DrawText(offscreen_canvas, font_thumb, 0, 25, green,
                                      f'{forecast_2.time} {forecast_2.temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
                    detail_length2 = graphics.DrawText(offscreen_canvas, font_thumb,
                                                       forecast_2.detail_text.pos, 31,
                                                       green,
                                                       f'{forecast_2.detail_text.text}')
                    forecast_2.detail_text.scroll(detail_length2)

                    # + 9 hour
                    graphics.DrawLine(offscreen_canvas, 0, 32, width - 1, 32, dark_blue)
                    forecast_4 = self.collection.forecast_list[offset + 4]
                    graphics.DrawText(offscreen_canvas, font_thumb, 0, 39, green,
                                      f'{forecast_4.time} {forecast_4.temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
                    detail_length3 = graphics.DrawText(offscreen_canvas, font_thumb,
                                                       forecast_4.detail_text.pos, 45,
                                                       green,
                                                       f'{forecast_4.detail_text.text}')
                    forecast_4.detail_text.scroll(detail_length3)

                    # + 12 hour
                    graphics.DrawLine(offscreen_canvas, 0, 46, width - 1, 46, dark_blue)
                    forecast_6 = self.collection.forecast_list[offset + 6]
                    graphics.DrawText(offscreen_canvas, font_thumb, 0, 53, green,
                                      f'{forecast_6.time} {forecast_6.temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
                    detail_length4 = graphics.DrawText(offscreen_canvas, font_thumb,
                                                       forecast_6.detail_text.pos, 59,
                                                       green,
                                                       f'{forecast_6.detail_text.text}')
                    forecast_6.detail_text.scroll(detail_length4)

                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_NEWS:
                    #                    graphics.DrawLine(offscreen_canvas, 0, 1, 63, 1, dark_blue)

                    for index, news_item in enumerate(self.collection.news_list):
                        #                        if news_item.delay < 1:
                        dep_color = green

                        y0 = index * 6 + 2
                        y1 = y0 + 5
                        text_length = graphics.DrawText(offscreen_canvas, font_thumb, news_item.text.pos, y1, dep_color,
                                                        news_item.text.text)
                        news_item.text.scroll(text_length)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)
            except Exception as e:
                self.logger.error('Failed to show display: %s', str(e))
                time.sleep(3)
