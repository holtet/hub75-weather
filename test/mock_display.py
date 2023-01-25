import logging


class MockDisplay:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def DrawText(canvas, font, x, y, color, text):
        logging.info(f'DrawText({font}, {x}, {y}, {color}, {text})')

    def DrawLine(canvas, x1, y1, x2, y2, color):
        logging.info(f'DrawLine({x1}, {y1} {x2}, {y2}, {color})')


class MockCanvas:
    pass
