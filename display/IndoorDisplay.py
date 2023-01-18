import logging
import os

from rgbmatrix import graphics
from PIL import Image
from config import Config
from display.Display import Display
from dto import DataCollection


class IndoorDisplay(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)
        self.home_image = Image.open("images/heart_house_24.bmp").convert('RGB')

        self.weather_icons = {}
        dir_path = 'images/weather'
        for path in os.listdir(dir_path):
            # check if current path is a file
            join = os.path.join(dir_path, path)
            if os.path.isfile(join):
                self.weather_icons[path] = Image.open(join).convert('RGB')

    def display(self, canvas):
        indoor = self.collection.indoor_environment_data
        outdoor = self.collection.current_weather_data

        graphics.DrawLine(canvas, 0, 6, self.config.zs_width, 6, self.grey)
        graphics.DrawLine(canvas, 60, 7, 60, 54, self.grey)
        graphics.DrawLine(canvas, 0, 54, self.config.zs_width, 54, self.grey)
        graphics.DrawText(canvas, self.font_5x7, 2, 5, self.light_blue, f'{self.collection.datetime}')

        temp_text_length = graphics.DrawText(canvas, self.font_6x12, 9, 16, self.green, f'{indoor.temperature:.1f} C')
        graphics.DrawCircle(canvas, temp_text_length - 0, 10, 1, self.green)
        graphics.DrawText(canvas, self.font_6x12, 9, 25, self.green, f'{indoor.humidity:.1f} %')
        #                    graphics.DrawText(canvas, font2, 1, 32, green, f'{indoor.pressure:.1f} hPa')
        canvas.SetImage(self.home_image, 12, 26)

        temp_text_length = graphics.DrawText(canvas, self.font_6x12, 73, 16, self.green, f'{outdoor.temperature} C')
        graphics.DrawCircle(canvas, temp_text_length + 63, 10, 1, self.green)
        graphics.DrawText(canvas, self.font_6x12, 73, 25, self.green, f'{outdoor.humidity} %')
        canvas.SetImage(self.weather_icons[f'{outdoor.icon}.bmp'], 81, 26)
        graphics.DrawText(canvas, self.font_thumb, 65, 50, self.green, f'{outdoor.weather_description}')

        graphics.DrawText(canvas, self.font_5x7, 0,
                          self.config.zs_height, self.green,
                          outdoor.detail_text2.text)
