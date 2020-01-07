import bme280
import smbus2
import time
import datetime
from os import wait
from threading import Thread, Event
import requests
import json
import aiohttp
import asyncio
from enturclient import EnturPublicTransportData
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from PIL import Image
from apds9960.const import *
from apds9960 import APDS9960
from dto import *
from const import *
import configparser
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler


class Coordinator(Thread):
    FADE_SECONDS = 2
    def __init__(self, event, collection: DataCollection, config: Config, scheduler: BackgroundScheduler):
        Thread.__init__(self)
        self.stopped = event
        self.collection = collection
        self.config = config
        self.scheduler = scheduler
        self.layout = TimePeriod("Default", [5, 5, 5, 5, 5, 5])
        
    def run(self):
#        layout = TimePeriod("Default", [15, 15, 30, 10, 10, 10])
        start_time =  time.perf_counter()
        drift = 0

        while not self.stopped.wait(0):
            pc = time.perf_counter() + self.collection.indoor_environment_data.time_offset
            secs_since_start = pc - start_time
            secs_since_rotation_start = secs_since_start % self.layout.total_rotation_secs
            time_count = 0
            prev_time_count = 0
            current_screen = -1
            while (time_count <= secs_since_rotation_start and current_screen < self.layout.max_screen):
                current_screen += 1
                prev_time_count = time_count
                time_count += self.layout.times[current_screen]

            secs_since_switch = secs_since_rotation_start - prev_time_count
            secs_until_switch = time_count - secs_since_rotation_start
            if secs_since_switch < self.FADE_SECONDS:
                self.collection.brightness = secs_since_switch / self.FADE_SECONDS
            elif secs_until_switch < self.FADE_SECONDS:
                 self.collection.brightness = secs_until_switch / self.FADE_SECONDS
            else:
                self.collection.brightness = 1
            self.collection.screen = current_screen
            self.collection.current_screen_time = secs_since_switch

            subsecond = (pc - start_time) % 1
            subsecond_half = subsecond - 0.5

            # On the "exact" second
            if(subsecond < 0.1):
                drift = subsecond
#                self.collection.datetime = datetime.datetime.today().strftime(self.config.datetime_format)#"%d/%m  %H:%M:%S")
                self.collection.datetime = datetime.datetime.today().strftime("%d/%m  %H:%M:%S")
#            print(f'{secs_since_rotation_start:.1f}, Screen:{current_screen}, timeCount:{time_count}, SSS:{secs_since_switch:.1f}, SUS:{secs_until_switch:.1f}, B:{self.collection.brightness:.1f})
            # On the "exact" half-second right before starting a new round through screens
            if(subsecond_half > 0 and subsecond_half < 0.01 and secs_until_switch < 1 and current_screen == self.layout.max_active_screen):
                self.find_next_timeperiod()
#                if tp != None:
#                    print(f'switching layout from {layout.layout} to {tp.layout}')
#                    self.check_pause_resume_job(layout.has_trains(), tp.has_trains(), TDF_JOB_ID)
#                    self.check_pause_resume_job(layout.has_forecast(), tp.has_forecast(), WFF_JOB_ID)
#                    self.check_pause_resume_job(layout.has_outdoor(), tp.has_outdoor(), CWF_JOB_ID)
#                    self.layout = tp
#                t = datetime.datetime.today()
#                print(f'current_screen {current_screen} max {layout.max_active_screen}')
#                print(f'min {t.minute} hour {t.hour} weekday {t.weekday()+1} day {t.day} month {t.month}')
#                for tp in self.config.time_periods:
#                    mmatch = tp.minutes == None or tp.minutes.__contains__(t.minute)
#                    hmatch = tp.hours == None or tp.hours.__contains__(t.hour)
#                    wdmatch = tp.weekdays == None or tp.weekdays.__contains__(t.weekday()+1)
#                    dmatch = tp.days == None or tp.days.__contains__(t.day)
#                    momatch = tp.months == None or tp.months.__contains__(t.month)
#                    print(f'time_period {str(tp)} matches: {mmatch and hmatch and wdmatch and dmatch and momatch}')
#                    if mmatch and hmatch and wdmatch and dmatch and momatch:
#                        if layout != tp:
            time.sleep(0.1-drift/10)

    def find_next_timeperiod(self):
        t = datetime.datetime.today()
                #print(f'current_screen {current_screen} max {layout.max_active_screen}')
                #print(f'min {t.minute} hour {t.hour} weekday {t.weekday()+1} day {t.day} month {t.month}')
        for tp in self.config.time_periods:
            mmatch = tp.minutes == None or tp.minutes.__contains__(t.minute)
            hmatch = tp.hours == None or tp.hours.__contains__(t.hour)
            wdmatch = tp.weekdays == None or tp.weekdays.__contains__(t.weekday()+1)
            dmatch = tp.days == None or tp.days.__contains__(t.day)
            momatch = tp.months == None or tp.months.__contains__(t.month)
                    #print(f'time_period {str(tp)} matches: {mmatch and hmatch and wdmatch and dmatch and momatch}')
            if mmatch and hmatch and wdmatch and dmatch and momatch:
                if self.layout != tp:
                    print(f'switching layout from {self.layout.layout} to {tp.layout}')
                    self.check_pause_resume_job(self.layout.has_trains(), tp.has_trains(), TDF_JOB_ID)
                    self.check_pause_resume_job(self.layout.has_forecast(), tp.has_forecast(), WFF_JOB_ID)
                    self.check_pause_resume_job(self.layout.has_outdoor(), tp.has_outdoor(), CWF_JOB_ID)
                    self.layout = tp
                    return
#                    return tp
#        return None
    
    def check_pause_resume_job(self, old, new, job_id):
        if (old and not new):
            print(f'Pausing {job_id}')
            self.scheduler.pause_job(job_id)
        elif (new and not old):
            print(f'Resuming {job_id}')
            self.scheduler.resume_job(job_id)
        

class WeatherForecastFetcher():
    
    def __init__(self, collection: DataCollection, config: Config):
#        Thread.__init__(self)
        self.collection = collection
#        self.stopped = event
        self.OWM_str_forecast = f'http://api.openweathermap.org/data/2.5/forecast?id={config.city_id}&appid={config.api_key}'

    def to_float_str(self, input):
        return str(round(float(input), 2))

    def run(self):
        if True:
#        while not self.stopped.wait(0):
            try:
                print("Fetching weather forecast")
                response = requests.get(self.OWM_str_forecast)#.json
#                print(response.content)
                response2 = response.json()
                if response2['cod'] != '404':
                    self.collection.forecast_list = []
                    forecasts = response2['list']
                    for forecast in forecasts:
                        fore = Forecast()
                        dt = datetime.datetime.fromtimestamp(forecast['dt'])
                        fore.weekday = dt.strftime('%a %d/%m')
                        fore.timestr = dt.strftime('%H:%M')
                        main = forecast['main']
                        fore.temp = str(round(float(main['temp'])-273.15, 2))
                        fore.weather_desc = forecast['weather'][0]['description']
                        fore.wind_speed = forecast['wind']['speed']
                        fore.clouds = forecast['clouds']['all']
                        if 'rain' in forecast and '3h' in forecast['rain']:
                                fore.rain_3h = float(forecast['rain']['3h'])
                        if 'snow' in forecast and '3h' in forecast['snow']:
                                fore.snow_3h = float(forecast['snow']['3h'])
                        fore.set_detail_text()
                        self.collection.forecast_list.append(fore)
#                    time.sleep(3600)
                else:
                    print("not found")
                    raise Exception
#                    time.sleep(600)
            except Exception as e:
                print(f'Weather forecast fetcher failed: {str(e)}')
                raise e
#                time.sleep(600)


def to_float_str(input):
    return str(round(float(input), 2))

def read_icon(cwd: CurrentWeatherData):
#    print(f'Loading icon {cwd.icon}.bmp')
    try:
        cwd.weather_icon = Image.open(f'{cwd.icon}.bmp').convert('RGB')
    except:
        print(f'Icon {cwd.icon} not found')
        cwd.weather_icon = Image.open('unknown.bmp').convert('RGB')


class CurrentWeatherFetcher:
    
    def __init__(self, collection: DataCollection, config: Config):
#        Thread.__init__(self)
        self.collection = collection
#        self.stopped = event
#        self.config = config
#        api_key = config["WEATHER"]["apiKey"]
#        city_id = config["WEATHER"]["cityId"]
        self.OWM_str_current = f'http://api.openweathermap.org/data/2.5/weather?id={config.city_id}&appid={config.api_key}'
    
    def run(self):
        if True:
            print("Fetching current weather")
#        while not self.stopped.wait(0):
#            sleep = 3600
            new_weather_data = CurrentWeatherData()
            try:
                x = requests.get(self.OWM_str_current).json()
                if x['cod'] != '404':
                    y = x['main']
                    new_weather_data.temperature = str(round(float(y['temp'])-273.15, 2))
                    new_weather_data.humidity = to_float_str(y['humidity'])
                    if 'sea_level' not in y:
                        new_weather_data.pressure = to_float_str(y['pressure'])
                    else:
                        new_weather_data.pressure = to_float_str(y['sea_level'])
                    z = x['weather']
                    new_weather_data.icon = z[0]['icon']
                    new_weather_data.weather_description = z[0]['description']
                    new_weather_data.city = x['name']
                    new_weather_data.wind_speed = x['wind']['speed']
                    if 'deg' in x['wind']:
                        new_weather_data.wind_dir = x['wind']['deg']
                    new_weather_data.clouds = x['clouds']['all']
                    if 'rain' in x:
                        rain = x['rain']
                        if '1h' in rain:
                            new_weather_data.rain_1h = float(rain['1h'])
                        if '3h' in rain:
                            new_weather_data.rain_3h = float(rain['3h'])
                    if 'snow' in x:
                        snow = x['snow']
                        if '1h' in snow:
                            new_weather_data.snow_1h = float(snow['1h'])
                        if '3h' in snow:
                            new_weather_data.snow_3h = float(snow['3h'])
                        
                    new_weather_data.set_header_text()
                    new_weather_data.set_detail_text2()                    
                else:
                    print("Current weather not found")
                    raise Exception("Current weather not found")
 #                   sleep = 600
            except Exception as e:
                print(f'Fetching current weather failed: {str(e)}')
                raise e
#                print(x)

#                sleep = 600
            read_icon(new_weather_data)
            self.collection.current_weather_data = new_weather_data
#            time.sleep(sleep)

            
class IndoorEnvironmentFetcherThread(Thread):
    PORT = 1  # i2c port
    ADDRESS = 0x76  # Adafruit BME280 address. Other BME280s may be different

    def __init__(self, event, collection: DataCollection):
        Thread.__init__(self)
        self.collection = collection
        self.stopped = event

    def run(self):
        bus = smbus2.SMBus(self.PORT)
        calibrated = False
        while not calibrated:
            try:
                bme280.load_calibration_params(bus, self.ADDRESS)
                calibrated = True
            except Exception as e:
                print(f'Failed to calibrate bme280 {str(e)}')
                time.sleep(5)
        apds = APDS9960(bus)
        apds.enableLightSensor()
#        apds.enableGestureSensor()
        while not self.stopped.wait(0):
            try:
                new_env_data = IndoorEnvironmentData()
                bme280_data = bme280.sample(bus, self.ADDRESS)
                new_env_data.humidity = bme280_data.humidity
                new_env_data.pressure = bme280_data.pressure
                new_env_data.temperature = bme280_data.temperature
                self.collection.indoor_environment_data = new_env_data
            except Exception as e:
                print(f'Failed to fetch indoor environment {str(e)}')

            try:
                self.collection.ambient_light = apds.readAmbientLight()
                if False:
                #                if apds.isGestureAvailable():
                    print(f"gesture available")
                    motion = apds.readGesture()
                    print(f"gesture code {motion}")
                    if(motion == APDS9960_DIR_UP):
                        new_env_data.time_offset += 15
                    elif(motion == APDS9960_DIR_DOWN):
                        new_env_data.time_offset -= 15
            except Exception as e:
                print(f'Failed to fetch brightness {str(e)}')

            time.sleep(1)
#                print("Gesture={}".format(dirs.get(motion, "unknown")))            
#            print(f'{self.collection.ambient_light}')


class MyPrinterThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(3):
            print("*")


class TrainDepartureFetcher:
#    API_CLIENT_ID = 'holtet-hub75display'

    def __init__(self, collection: DataCollection, config: Config):
#        Thread.__init__(self)
#        self.stopped = event
        self.collection = collection
        self.config = config

    def run(self):
        if True:
            print("Fetching train departures")
#        while not self.stopped.wait(0):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.print_train_delay())
            except Exception as e:
                print(f'Failed to fetch train times {str(e)}')
                raise e
#            time.sleep(300)

    async def print_train_delay(self):
        async with aiohttp.ClientSession() as client:
            stop_id = f'NSR:StopPlace:{self.config.stop_id}'
            stops = [stop_id]
            data = EnturPublicTransportData(
                client_name=self.config.entur_client_id,
                stops=stops,
                omit_non_boarding=True,
                number_of_departures=10,
                web_session=client)
            await data.update()

            train = data.get_stop_info(stop_id)
            dindex = 0
            for index, call in enumerate(train.estimated_calls):
#                print(f'|{call.front_display}|')
#                for d in self.destinations:
#                    print(f'destination: |{d}|')
                if dindex < 5 and call.front_display in self.config.destinations:# or (1 == 1):
                    old_pos = self.collection.departure_list[dindex].pos
                    departure = Departure(call.front_display, call.aimed_departure_time, call.delay_in_min, old_pos)
                    self.collection.departure_list[dindex] = departure
                    dindex += 1
#                else:
#                    print(f'Skipped train departure |{call.front_display}|, dindex {dindex}')
            while dindex < 5:
                self.collection.departure_list[dindex] = Departure("", "", 0, 0)
                dindex += 1

                
class LedDisplayThread(Thread):
    def __init__(self, event, collection: DataCollection):
        Thread.__init__(self)
        self.stopped = event
        self.collection = collection

    def run(self):
        print("Starting display thread")
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'                                                                       
        matrix = RGBMatrix(options = options)
        
        offscreen_canvas = matrix.CreateFrameCanvas()
        
        font = graphics.Font()
        font.LoadFont("rpi-rgb-led-matrix/fonts/tom-thumb.bdf")
        font2 = graphics.Font()
        font2.LoadFont("rpi-rgb-led-matrix/fonts/6x12.bdf")

        font3 = graphics.Font()
        font3.LoadFont("rpi-rgb-led-matrix/fonts/4x6.bdf")

        font4 = graphics.Font()
        font4.LoadFont("rpi-rgb-led-matrix/fonts/6x9.bdf")

        home_image = Image.open("blue_house1.bmp").convert('RGB')

        black = graphics.Color(0, 0, 0)
        red = graphics.Color(128 , 0, 0)
        purple = graphics.Color(28 , 65, 84)
        lightBlue = graphics.Color(0, 0, 128)
        darkBlue = graphics.Color(0, 0, 32)
        green = graphics.Color(0, 128, 0)
        orange = graphics.Color(128, 75, 0)

        while True:
            try:
                offscreen_canvas.Clear()
                offscreen_canvas.brightness = self.collection.brightness * min(self.collection.ambient_light*2+10, 100)
                if (self.collection.screen == SCREEN_TRAINS):
                    graphics.DrawLine(offscreen_canvas, 0, 1, 63, 1, darkBlue)

                    for index, dep in enumerate(self.collection.departure_list, start=0):
                        if (dep.delay < 1):
                            dep_color = green
                        elif (dep.delay < 8):
                            dep_color = orange
                        else:
                            dep_color = red

                        y0 = index * 6 + 2
                        y1 = y0 + 5
                        text_length = graphics.DrawText(offscreen_canvas, font, dep.display.pos, y1, dep_color, dep.text1())
                        dep.display.scroll(text_length)
                        for y in range(y0, y1):
                            graphics.DrawLine(offscreen_canvas, 45, y, 63, y, black)
                            graphics.DrawLine(offscreen_canvas, 45 - 1, y0, 45 - 1, y1, darkBlue)
                            graphics.DrawLine(offscreen_canvas, 0, y1, 63, y1, darkBlue)
                            graphics.DrawText(offscreen_canvas, font, 45, y1, dep_color, dep.text2())
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)                                                
                elif (self.collection.screen == SCREEN_INDOOR):
                    graphics.DrawLine(offscreen_canvas, 0, 5, 63, 5, darkBlue)
                    graphics.DrawText(offscreen_canvas, font, 2, 5, red, f'{self.collection.datetime}')
                    indoor = self.collection.indoor_environment_data
                    temp_text_length  = graphics.DrawText(offscreen_canvas, font2, 0, 14, green, f'{indoor.temperature:.2f} C')
                    graphics.DrawText(offscreen_canvas, font2, 0, 23, green, f'{indoor.humidity:.2f} %')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 8, 8, 1, green)
                    graphics.DrawText(offscreen_canvas, font2, 0, 32, green, f'{indoor.pressure:.1f} hPa')
                    offscreen_canvas.SetImage(home_image, 45, 7)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.1)

                elif (self.collection.screen == SCREEN_OUTDOOR):
                    outdoor = self.collection.current_weather_data
                    graphics.DrawLine(offscreen_canvas, 0, 5, 63, 5, darkBlue)
                    header_text_length = graphics.DrawText(offscreen_canvas, font, outdoor.header_text.pos, 5, red, outdoor.header_text.text)
                    outdoor.header_text.scroll(header_text_length)
                    temp_text_length  = graphics.DrawText(offscreen_canvas, font2, 0, 14, green, f'{outdoor.temperature} C')
                    graphics.DrawCircle(offscreen_canvas, temp_text_length - 8, 8, 1, green)
                    graphics.DrawText(offscreen_canvas, font2, 0, 23, green, f'{outdoor.humidity} %')
                    offscreen_canvas.SetImage(outdoor.weather_icon, 45, 7)

#                detail1_length = graphics.DrawText(offscreen_canvas, font, outdoor.detail_text1.pos, 25, green, outdoor.detail_text1.text)
#                outdoor.detail_text1.scroll(detail1_length)
                    detail2_length = graphics.DrawText(offscreen_canvas, font2, outdoor.detail_text2.pos, 31, green, outdoor.detail_text2.text)
                    outdoor.detail_text2.scroll(detail2_length)                
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)

#                elif (self.collection.screen in [SCREEN_FORECAST_1, SCREEN_FORECAST_2, SCREEN_FORECAST_3]):
                elif (self.collection.screen == SCREEN_FORECAST_1 or self.collection.screen == SCREEN_FORECAST_2 or self.collection.screen == SCREEN_FORECAST_3):
                    offset = 0
                    if(self.collection.screen == SCREEN_FORECAST_2):
                        offset = 4
                    elif(self.collection.screen == SCREEN_FORECAST_3):
                        offset = 8
                    graphics.DrawLine(offscreen_canvas, 0, 5, 63, 5, darkBlue)
                    graphics.DrawText(offscreen_canvas, font, 0, 5, purple, f'{self.collection.current_weather_data.city}  {self.collection.forecast_list[offset].weekday}')

                    graphics.DrawText(offscreen_canvas, font, 0, 11, green, f'{self.collection.forecast_list[offset].timestr} {self.collection.forecast_list[offset].temp}C')
#                graphics.DrawText(offscreen_canvas, font, 0, 17, green, f'{self.collection.forecast_list[offset].weather_desc}')
                    detail_length1 = graphics.DrawText(offscreen_canvas, font, self.collection.forecast_list[offset].detail_text.pos, 17, green, f'{self.collection.forecast_list[offset].detail_text.text}')
                    self.collection.forecast_list[offset].detail_text.scroll(detail_length1)
                    graphics.DrawLine(offscreen_canvas, 0, 18, 63, 18, darkBlue)
                    graphics.DrawText(offscreen_canvas, font, 0, 25, green, f'{self.collection.forecast_list[offset+2].timestr} {self.collection.forecast_list[offset+2].temp}C')
#                graphics.DrawText(offscreen_canvas, font, 0, 31, green, f'{self.collection.forecast_list[offset+2].weather_desc}')
                    detail_length2 = graphics.DrawText(offscreen_canvas, font, self.collection.forecast_list[offset+2].detail_text.pos, 31, green, f'{self.collection.forecast_list[offset+2].detail_text.text}')
                    self.collection.forecast_list[offset+2].detail_text.scroll(detail_length2)
                    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
                    time.sleep(0.03)            
            except Exception as e:
                print(f'Failed to fetch print {str(e)}')
                time.sleep(3)

class Listener:
    def __init__(self, joblist):
        self.joblist = joblist

    def job_done_listener(self, event):
        job = joblist[event.job_id]
        if event.exception:
            print(f'The job {event.job_id} crashed')
            if job.last_success == True:
                job.job.reschedule(trigger='interval', seconds=interval_error)
                job.last_success = False
        else:
            print(f'The job {event.job_id} was successful')
            if job.last_success == False:
                job.job.reschedule(trigger='interval', seconds=interval_ok)
                job.last_success = True

                                                                                                                                        
# Main function
if __name__ == "__main__":
    configp = configparser.ConfigParser()
    configp.read('config.ini')
    config = Config(configp)
    
    dataCollection = DataCollection()

    job_defaults = {
        'coalesce': True
    }

    scheduler = BackgroundScheduler(job_defaults = job_defaults)
    joblist = {}

    wff = WeatherForecastFetcher(dataCollection, config)
    wff.run()
    wff_job = scheduler.add_job(wff.run, trigger='interval', seconds=3600, id=WFF_JOB_ID)
    joblist[WFF_JOB_ID] = Job(wff_job, 3600, 600)
#    scheduler.add_listener(Listeners(wff_job, 3600, 600).my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#    jobs.wff_job = wff_job
    
    tdf = TrainDepartureFetcher(dataCollection, config)
    tdf.run()
    tdf_job = scheduler.add_job(tdf.run, trigger='interval', seconds=300, id=TDF_JOB_ID)
    joblist[TDF_JOB_ID] = Job(tdf_job, 300, 150)

    cwf = CurrentWeatherFetcher(dataCollection, config)
    cwf.run()
    cwf_job = scheduler.add_job(cwf.run, trigger='interval', seconds=3600, id=CWF_JOB_ID)
    joblist[CWF_JOB_ID] = Job(cwf_job, 3600, 600)

    scheduler.add_listener(Listener(joblist).job_done_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#    jobs.tdf_job = tdf_job
    
    scheduler.start()
    
    stopFlag = Event()

#    thread1 = TrainDepartureFetcherThread(stopFlag, dataCollection, config)
#    thread1.start()

    thread3 = IndoorEnvironmentFetcherThread(stopFlag, dataCollection)
    thread3.start()

    thread4 = Coordinator(stopFlag, dataCollection, config, scheduler)
    thread4.start()

#    thread5 = CurrentWeatherFetcherThread(stopFlag, dataCollection, config)
#    thread5.start()

#    thread6 = WeatherForecastFetcherThread(stopFlag, dataCollection, config)
#    thread6.start()
    
    run_text = LedDisplayThread(stopFlag, dataCollection)
    run_text.start()
#    if (not run_text.process()):
#        run_text.print_help()

#    stopFlag.set()
#    thread1.join()
#    thread3.join()
#    thread4.join()
#    thread5.join()
#    thread6.join()
