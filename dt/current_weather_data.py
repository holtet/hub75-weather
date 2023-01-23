from dt.scroll_text import ScrollText


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
        self.detail_text1 = ScrollText(f'Wind:{self.wind_speed}m/s  Cloud%:{self.clouds}', 0, 128, 128)

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
        # {snow_text}
        # {rain_text}
        self.detail_text2 = ScrollText(
            f'Wind {self.wind_speed}m/s  Clouds {self.clouds}%', 0,
            128, 128)
        # {self.pressure} hPa  TODO: Farge avh av vær
