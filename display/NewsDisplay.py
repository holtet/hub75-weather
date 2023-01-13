import logging
from typing import List

from rgbmatrix import graphics

from config import Config
from display.Display import Display
from dto import NewsItem


class NewsDisplay(Display):

    def __init__(self, config: Config, news_list: List[NewsItem]):
        self.config = config
        self.news_list = news_list
        self.logger = logging.getLogger(__name__)

    def display(self, canvas):
        for index, news_item in enumerate(self.news_list):
            y0 = index * 6 + 2
            y1 = y0 + 5
            text_length = graphics.DrawText(canvas, self.font_thumb, news_item.text.pos, y1, self.green,
                                            news_item.text.text)
            news_item.text.scroll(text_length)
