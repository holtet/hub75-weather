import logging
from typing import List

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dto import NewsItem, DataCollection


class NewsDisplay(Display):

    def __init__(self, config: Config, collection: DataCollection):
        self.config = config
        self.collection = collection
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        for index, news_item in enumerate(self.collection.news_list):
            y0 = index * 6 + 2
            y1 = y0 + 5
            text_length = graphics.DrawText(canvas, self.font_thumb, news_item.text.pos, y1, self.green,
                                            news_item.text.text)
            news_item.text.scroll(text_length)
