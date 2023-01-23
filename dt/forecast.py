from dt.scroll_text import ScrollText


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
