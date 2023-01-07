import datetime
import functools
import operator

from const import *
from dt.electricity_prices import ElectricityPrices


class NewsItem:
    def __init__(self, text):
        self.text = ScrollText(text, 0, 128, 128)


class Job:
    def __init__(self, job, interval_ok, interval_error):
        self.job = job
        self.last_success = True
        self.interval_ok = interval_ok
        self.interval_error = interval_error


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


class Forecast:
    def __init__(self):  # , weekday, timestr, temp, weather_desc):
        self.weekday = ''  # weekday
        self.time = ''  # timestr
        self.temp = ''  # temp
        self.weather_desc = ''  # weather_desc
        self.detail_text = ScrollText('', 0, 0, 0)
        self.wind_speed = ''
        self.wind_dir = ''
        self.clouds = ''
        #        self.rain_1h = 0.0
        self.rain_3h = 0.0
        #        self.snow_1h = 0.0
        self.snow_3h = 0.0

    def set_detail_text(self):
        rain_text = ""
        snow_text = ""
        #        print(f'{self.snow_1h} type {type(self.snow_1h)} {self.rain_1h > 0.0}')
        if self.snow_3h > 0.0:
            snow_text = f'Snow_3h: {self.snow_3h} '
        #        elif(self.rain_1h > 0.0):
        #            rain_text = f'Rain 1h: {self.rain_1h}mm Rain 3h: {self.rain_3h}mm '
        if self.rain_3h > 0.0:
            rain_text = f'Rain 3h: {self.rain_3h}mm '
        self.detail_text = ScrollText(
            f'{self.weather_desc}, {snow_text}{rain_text}Wind: {self.wind_speed}m/s  Clouds: {self.clouds}%', 0, 128,
            30)


class ScrollText:
    def __init__(self, text, left, right, start_pos):
        self.text = text
        self.left = left
        self.right = right
        self.pos = start_pos

    def scroll(self, text_length):
        self.pos -= 1
        if self.pos + text_length < self.left:
            self.pos = self.right


# class Departure2:
#     def __init__(self, display, time, delay, pos):
#         self.display = display
#         self.time = time.strftime("%H:%M")
#         self.delay = delay
#         self.pos = pos
#
#     def text1(self):
#         #        print(f'{self.display} Pos {self.pos}')
#         self.pos -= 1
#         if self.delay == 0:
#             return f'{self.display}'
#         else:
#             return f'{self.display}  ({str(self.delay)}m)'
#
#     def text2(self):
#         return f'{self.time}'


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


class IndoorEnvironmentData:
    def __init__(self):
        self.temperature = 0.0
        self.humidity = 0.0
        self.pressure = 0.0
        self.time_offset = 0


class CurrentWeatherData:
    def __init__(self):
        self.temperature = "--.-"
        self.humidity = "--.-"
        self.pressure = "--.-"
        self.icon = 'unknown'
        self.city = '-'
        self.weather_description = '-'
        self.weather_icon = ''
        self.header_text = ScrollText('', 0, 0, 0)
        self.detail_text1 = ScrollText('', 0, 0, 0)
        self.detail_text2 = ScrollText('', 0, 0, 0)
        self.wind_speed = ''
        self.wind_dir = ''
        self.clouds = ''
        self.rain_1h = 0.0
        self.rain_3h = 0.0
        self.snow_1h = 0.0
        self.snow_3h = 0.0

    def set_header_text(self):
        self.header_text = ScrollText(f'{self.city}: {self.weather_description}', 0, 128, 128)

    def set_detail_text1(self):
        self.detail_text1 = ScrollText(f'Wind: {self.wind_speed}m/s  Cloud%: {self.clouds}', 0, 128, 128)

    def set_detail_text2(self):
        rain_text = ""
        snow_text = ""
        #        print(f'{self.snow_1h} type {type(self.snow_1h)} {self.rain_1h > 0.0}')
        if self.snow_1h > 0.0:
            snow_text = f'Snow_1h: {self.snow_1h}mm '
        elif self.rain_1h > 0.0:
            rain_text = f'Rain 1h: {self.rain_1h}mm Rain 3h: {self.rain_3h}mm '
        elif self.rain_3h > 0.0:
            rain_text = f'Rain 3h: {self.rain_3h}mm '
        self.detail_text2 = ScrollText(
            f'{self.weather_description} {snow_text}{rain_text}Wind: {self.wind_speed}m/s  Clouds: {self.clouds}%', 0,
            128, 128)
        # {self.pressure} hPa  TODO: Farge avh av vær


class DataCollection:
    def __init__(self):
        self.brightness = 0
        self.datetime = ""
        self.screen = 0
        self.current_screen_time = 0
        self.indoor_environment_data = IndoorEnvironmentData()
        self.current_weather_data = CurrentWeatherData()
        self.electricity_prices = ElectricityPrices()
        self.departure_list = []
        self.news_list = []
        for i in range(0, 8):
            self.departure_list.append(Departure("", datetime.time(0, 0, 0), 0, 128))
            self.news_list.append(NewsItem(""))
        self.ambient_light = 100
        self.forecast_list = []
