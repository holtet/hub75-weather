import datetime
import time

class Forecast:
    def __init__(self): #, weekday, timestr, temp, weather_desc):
        self.weekday = ''#weekday
        self.timestr = ''#timestr
        self.temp = '' #temp
        self.weather_desc = ''#weather_desc
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
        if(self.snow_3h > 0.0):
            snow_text = f'Snow_3h: {self.snow_3h} '
#        elif(self.rain_1h > 0.0):
#            rain_text = f'Rain 1h: {self.rain_1h}mm Rain 3h: {self.rain_3h}mm '
        if(self.rain_3h > 0.0):
            rain_text = f'Rain 3h: {self.rain_3h}mm '
        self.detail_text = ScrollText(f'{self.weather_desc}  {snow_text}{rain_text}Wind: {self.wind_speed}m/s  Clouds: {self.clouds}%', 0, 64, 64)

        
class ScrollText:
    def __init__(self, text, left, right, start_pos):
        self.text = text
        self.left = left
        self.right = right
        self.pos = start_pos

    def scroll(self, text_length):
        self.pos -= 1
        if(self.pos + text_length < self.left):
            self.pos = self.right


class Departure2:
    def __init__(self, display, time, delay, pos):
        self.display = display
        self.time = time.strftime("%H:%M")
        self.delay = delay
        self.pos = pos 

    def text1(self):
#        print(f'{self.display} Pos {self.pos}')
        self.pos -= 1
        if(self.delay == 0):
            return f'{self.display}'
        else:
            return f'{self.display}  ({str(self.delay)}m)'

    def text2(self):
        return f'{self.time}'

    
class Departure:
    def __init__(self, display, time, delay, pos):
        self.display = ScrollText(display, 0, 45, pos)
        if(isinstance(time, str)):
            self.time = time
        else:
            self.time = time.strftime("%H:%M")
        self.delay = delay
        self.pos = pos

    def text1(self):
#        print(f'{self.display.text} Pos {self.display.pos}')
#        self.pos -= 1
        if(self.delay == 0):
            return f'{self.display.text}'
        else:
            return f'{self.display.text}  ({str(self.delay)}m)'

    def text2(self):
        return f'{self.time}'


class IndoorEnvironmentData():
    def __init__(self):
        self.temperature = 0.0
        self.humidity = 0.0
        self.pressure = 0.0
        self.time_offset = 0

        
class CurrentWeatherData():
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
        self.header_text = ScrollText(f'{self.city}: {self.weather_description}', 0, 64, 64)
    def set_detail_text1(self):
        self.detail_text1 = ScrollText(f'Wind: {self.wind_speed}m/s  Cloud%: {self.clouds}', 0, 64, 64)
    def set_detail_text2(self):
        rain_text = ""
        snow_text = ""
#        print(f'{self.snow_1h} type {type(self.snow_1h)} {self.rain_1h > 0.0}')
        if(self.snow_1h > 0.0):
            snow_text = f'Snow_1h: {self.snow_1h}mm '
        elif(self.rain_1h > 0.0):
            rain_text = f'Rain 1h: {self.rain_1h}mm Rain 3h: {self.rain_3h}mm '
        elif(self.rain_3h > 0.0):
            rain_text = f'Rain 3h: {self.rain_3h}mm '
        self.detail_text2 = ScrollText(f'{self.pressure} hPa  {snow_text}{rain_text}Wind: {self.wind_speed}m/s  Clouds: {self.clouds}%', 0, 64, 64)
        #TODO: Farge avh av vær

        
class DataCollection():
    def __init__(self):
        self.brightness = 0
        self.datetime = ""
        self.screen = 0
        self.current_screen_time = 0
        self.indoor_environment_data = IndoorEnvironmentData()
        self.current_weather_data = CurrentWeatherData()
        self.departure_list = []
        for i in range(0, 5):
            self.departure_list.append(Departure("", datetime.time(0, 0, 0), 0, 64))
        self.ambient_light = 100
        self.forecast_list = []
