import functools
import operator

from const import SCREEN_TRAINS, SCREEN_OUTDOOR, SCREEN_FORECAST_1, SCREEN_FORECAST_2, SCREEN_FORECAST_3, SCREEN_NEWS


class TimePeriod:
    def __init__(self, layout, times):
        self.times = times
        self.layout = layout
        self.minutes = None
        self.hours = []
        self.weekdays = None
        self.days = None
        self.months = None
        self.max_screen = len(times)
        self.max_active_screen = next(filter(lambda b: b[1] > 0, reversed(list(enumerate(times)))), (0, 0))[0]
        #        self.max_active_screen = len(list(filter(lambda x: x > 0, times))) - 1
        self.total_rotation_secs = functools.reduce(operator.add, times)

    def has_trains(self):
        return self.times[SCREEN_TRAINS] > 0

    def has_outdoor(self):
        return self.times[SCREEN_OUTDOOR] > 0

    def has_forecast(self):
        return self.times[SCREEN_FORECAST_1] > 0 or self.times[SCREEN_FORECAST_2] > 0 or self.times[
            SCREEN_FORECAST_3] > 0

    def has_news(self):
        return self.times[SCREEN_NEWS] > 0

    def __str__(self):
        return f'layout {self.layout} minutes {self.minutes} hours {self.hours} weekdays {self.weekdays} days {self.days} months {self.months} -> {self.times}'
