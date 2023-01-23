from dt.scroll_text import ScrollText


class Departure:
    def __init__(self, display, time, delay, pos):
        self.display = ScrollText(display, 0, 45 + 64, pos)
        if isinstance(time, str):
            self.time = time
        else:
            self.time = time.strftime("%H:%M")
        self.delay = delay
        self.pos = pos

    def train_name(self):
        #        print(f'{self.display.text} Pos {self.display.pos}')
        #        self.pos -= 1
        if self.delay == 0:
            return f'{self.display.text}'
        else:
            return f'{self.display.text}  ({str(self.delay)}m)'

    def departure_time(self):
        return f'{self.time}'
