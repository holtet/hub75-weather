from rgbmatrix import graphics


class Display:
    # rød og blå er byttet
    black = graphics.Color(0, 0, 0)
    extra_light_blue = graphics.Color(192, 64, 64)
    light_blue = graphics.Color(127, 0, 0)
    dark_blue = graphics.Color(96, 16, 16)
    purple = graphics.Color(84, 65, 28)
    purple2 = graphics.Color(78, 0, 78)
    green = graphics.Color(0, 127, 0)
    grey = graphics.Color(20, 20, 20)
    white = graphics.Color(127, 127, 127)
    orange = graphics.Color(0, 75, 127)
    red = graphics.Color(0, 0, 127)

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
