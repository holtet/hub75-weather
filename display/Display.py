from rgbmatrix import graphics


class Display:
    black = graphics.Color(0, 0, 0)
    dark_blue = graphics.Color(0, 0, 127)
    purple = graphics.Color(28, 65, 84)
    light_blue = graphics.Color(78, 0, 78)
    green = graphics.Color(0, 127, 0)
    grey = graphics.Color(20, 20, 20)
    white = graphics.Color(127, 127, 127)
    orange = graphics.Color(127, 75, 0)
    red = graphics.Color(127, 0, 0)

    font_thumb = graphics.Font()
    font_thumb.LoadFont("../rpi-rgb-led-matrix/fonts/tom-thumb.bdf")

    font_4x6 = graphics.Font()
    font_4x6.LoadFont("rpi-rgb-led-matrix/fonts/4x6.bdf")

    font_5x7 = graphics.Font()
    font_5x7.LoadFont("rpi-rgb-led-matrix/fonts/5x7.bdf")

    font_6x9 = graphics.Font()
    font_6x9.LoadFont("rpi-rgb-led-matrix/fonts/6x9.bdf")

    font_6x12 = graphics.Font()
    font_6x12.LoadFont("rpi-rgb-led-matrix/fonts/6x12.bdf")
