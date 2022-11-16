import logging 
import time 
from threading import Thread 
from PIL import Image 
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions 
from dto import *


class LedDisplayThread(Thread):
    def __init__(self, collection: DataCollection):
        Thread.__init__(self)
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

        font = graphics.Font()
        font.LoadFont("rpi-rgb-led-matrix/fonts/tom-thumb.bdf")
        font2 = graphics.Font()
        font2.LoadFont("rpi-rgb-led-matrix/fonts/6x12.bdf")

        font3 = graphics.Font()
        font3.LoadFont("rpi-rgb-led-matrix/fonts/4x6.bdf")

        font4 = graphics.Font()
        font4.LoadFont("rpi-rgb-led-matrix/fonts/6x9.bdf")

        home_image = Image.open("heart_house.bmp").convert('RGB')

        black = graphics.Color(0, 0, 0)
        red = graphics.Color(128, 0, 0)
        purple = graphics.Color(28, 65, 84)
        lightBlue = graphics.Color(0, 0, 128)
        dark_blue = graphics.Color(0, 0, 32)
        green = graphics.Color(0, 128, 0)
        orange = graphics.Color(128, 75, 0)

        while True:
            try:
                offscreen_canvas.Clear()
                offscreen_canvas.brightness = \
                    self.collection.brightness * min(self.collection.ambient_light * 2 + 10, 100)

                if self.collection.screen == SCREEN_TRAINS:
                    graphics.DrawLine(offscreen_canvas, 0, 1, width - 1, 1, dark_blue)

                    for index, dep in enumerate(self.collection.departure_list, start=0):
                        if dep.delay < 1:
                            dep_color = green
                        elif dep.delay < 8:
                            dep_color = orange
                        else:
                            dep_color = red

                        y0 = index * 6 + 2
                        y1 = y0 + 5
                        text_length = graphics.DrawText(offscreen_canvas, font, 0, y1, dep_color,
                                                         dep.text1())
#                        text_length = graphics.DrawText(offscreen_canvas, font, dep.display.pos, y1, dep_color,
#                                                         dep.text1())
#                        dep.display.scroll(text_length)
                        for y in range(y0, y1):
                            graphics.DrawLine(offscreen_canvas, width-19, y, width-1, y, black)
                        graphics.DrawLine(offscreen_canvas, width-20, y0, width-20, y1, dark_blue)
                        graphics.DrawLine(offscreen_canvas, 0, y1, width-1, y1, dark_blue)
                        graphics.DrawText(offscreen_canvas, font, width-19, y1, dep_color, dep.text2())
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_INDOOR:
                    graphics.DrawLine(offscreen_canvas, 0, 5, width - 1, 5, dark_blue)
                    graphics.DrawText(offscreen_canvas, font, 2, 5, red, f'{self.collection.datetime}')
                    indoor = self.collection.indoor_environment_data
                    outdoor = self.collection.current_weather_data
                    temp_text_length = graphics.DrawText(offscreen_canvas, font2, 1, 14, green,
                                                         f'{indoor.temperature:.1f} C')
                    graphics.DrawText(offscreen_canvas, font2, 1, 23, green, f'{indoor.humidity:.1f} %')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 8, 8, 1, green)
#                    graphics.DrawText(offscreen_canvas, font2, 1, 32, green, f'{indoor.pressure:.1f} hPa')
#                    graphics.DrawText(offscreen_canvas, font, 1, 32, green, outdoor.weather_description)
                    detail2_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text2.pos, height - 2, green,
                                                       outdoor.detail_text2.text)
                    outdoor.detail_text2.scroll(detail2_length)
                    offscreen_canvas.SetImage(home_image, 45, 7)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_OUTDOOR:
                    outdoor = self.collection.current_weather_data
                    graphics.DrawLine(offscreen_canvas, 0, 5, width-1, 5, dark_blue)
                    graphics.DrawText(offscreen_canvas, font, 2, 5, red, f'{self.collection.datetime}')
#                    header_text_length = graphics.DrawText(offscreen_canvas, font, outdoor.header_text.pos, 5, red,
#                                                           outdoor.header_text.text)
#                    outdoor.header_text.scroll(header_text_length)
                    temp_text_length = graphics.DrawText(offscreen_canvas, font2, 1, 14, green,
                                                         f'{outdoor.temperature} C')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 8, 8, 1, green)
                    graphics.DrawText(offscreen_canvas, font2, 1, 23, green, f'{outdoor.humidity} %')
                    offscreen_canvas.SetImage(outdoor.weather_icon, 45, 7)

                    #                detail1_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text1.pos, 25, green, outdoor.detail_text1.text)
                    #                outdoor.detail_text1.scroll(detail1_length)
                    detail2_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text2.pos, height - 2, green,
                                                       outdoor.detail_text2.text)
                    outdoor.detail_text2.scroll(detail2_length)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                #                elif (self.collection.screen in [SCREEN_FORECAST_1, SCREEN_FORECAST_2, SCREEN_FORECAST_3]):
                elif (
                        self.collection.screen == SCREEN_FORECAST_1
                        or self.collection.screen == SCREEN_FORECAST_2
                        or self.collection.screen == SCREEN_FORECAST_3):
                    offset = 0
                    if self.collection.screen == SCREEN_FORECAST_2:
                        offset = 4
                    elif self.collection.screen == SCREEN_FORECAST_3:
                        offset = 8
                    graphics.DrawLine(offscreen_canvas, 0, 5, width-1, 5, dark_blue)
                    graphics.DrawText(offscreen_canvas, font, 0, 5, purple,
                                      f'{self.collection.current_weather_data.city}  {self.collection.forecast_list[offset].weekday}')

                    graphics.DrawText(offscreen_canvas, font, 0, 11, green,
                                      f'{self.collection.forecast_list[offset].timestr} {self.collection.forecast_list[offset].temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 17, green, f'{self.collection.forecast_list[offset].weather_desc}')
                    detail_length1 = graphics.DrawText(offscreen_canvas, font,
                                                       self.collection.forecast_list[offset].detail_text.pos, 17, green,
                                                       f'{self.collection.forecast_list[offset].detail_text.text}')
                    self.collection.forecast_list[offset].detail_text.scroll(detail_length1)
                    graphics.DrawLine(offscreen_canvas, 0, 18, width-1, 18, dark_blue)
                    graphics.DrawText(offscreen_canvas, font, 0, 25, green,
                                      f'{self.collection.forecast_list[offset + 2].timestr} {self.collection.forecast_list[offset + 2].temp}C')
                    #                graphics.DrawText(offscreen_canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
                    detail_length2 = graphics.DrawText(offscreen_canvas, font,
                                                       self.collection.forecast_list[offset + 2].detail_text.pos, 31,
                                                       green,
                                                       f'{self.collection.forecast_list[offset + 2].detail_text.text}')
                    self.collection.forecast_list[offset + 2].detail_text.scroll(detail_length2)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

                elif self.collection.screen == SCREEN_NEWS:
#                    graphics.DrawLine(offscreen_canvas, 0, 1, 63, 1, dark_blue)

                    for index, dep in enumerate(self.collection.news_list, start=0):
#                        if dep.delay < 1:
                        dep_color = green

                        y0 = index * 6 + 2
                        y1 = y0 + 5
                        text_length = graphics.DrawText(offscreen_canvas, font, dep.text.pos, y1, dep_color,
                                                        dep.text.text)
                        dep.text.scroll(text_length)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)
            except Exception as e:
                self.logger.error('Failed to show display: %s', str(e))
                time.sleep(3)
