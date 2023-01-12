from rgbmatrix import graphics


class Display:
    dark_blue = graphics.Color(0, 0, 132)
    purple = graphics.Color(28, 65, 84)
    light_blue = graphics.Color(78, 0, 78)
#    dark_blue = graphics.Color(0, 0, 32)
    green = graphics.Color(0, 128, 0)
    grey = graphics.Color(32, 32, 32)
    white = graphics.Color(128, 128, 128)

    font_thumb = graphics.Font()
    font_thumb.LoadFont("../rpi-rgb-led-matrix/fonts/tom-thumb.bdf")
