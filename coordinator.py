import logging
import time
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from dto import *
from config import Config

class Coordinator(Thread):
    FADE_SECONDS = 2

    def __init__(self, collection: DataCollection, config: Config, scheduler: BackgroundScheduler):
        Thread.__init__(self)
        self.collection = collection
        self.config = config
        self.scheduler = scheduler
        self.layout = TimePeriod("Default", [5, 5, 5, 5, 5, 5, 5])
        self.logger = logging.getLogger(__name__)

    def run(self):
        start_time = time.perf_counter()
        drift = 0

        while True:
            pc = time.perf_counter() + self.collection.indoor_environment_data.time_offset
            secs_since_start = pc - start_time
            secs_since_rotation_start = secs_since_start % self.layout.total_rotation_secs
            time_count = 0
            prev_time_count = 0
            current_screen = -1
            while time_count <= secs_since_rotation_start and current_screen < self.layout.max_screen:
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
            if subsecond < 0.1:
                drift = subsecond
                self.collection.datetime = datetime.datetime.today().strftime(self.config.datetime_format)
                # #"%d/%m  %H:%M:%S")
                #self.collection.datetime = datetime.datetime.today().strftime("%d/%m  %H:%M:%S")
            # print(f'{secs_since_rotation_start:.1f}, Screen:{current_screen}, timeCount:{time_count},
            # SSS:{secs_since_switch:.1f}, SUS:{secs_until_switch:.1f}, B:{self.collection.brightness:.1f})
            # On the "exact" half-second right before starting a new round through screens
            if (
                    0 < subsecond_half < 0.01
                    and secs_until_switch < 1
                    and current_screen == self.layout.max_active_screen):
                self.find_next_timeperiod()
            time.sleep(0.1 - drift / 10)

    def find_next_timeperiod(self):
        t = datetime.datetime.today()
        # print(f'current_screen {current_screen} max {layout.max_active_screen}')
        # print(f'min {t.minute} hour {t.hour} weekday {t.weekday()+1} day {t.day} month {t.month}')
        for tp in self.config.time_periods:
            mmatch = tp.minutes is None or tp.minutes.__contains__(t.minute)
            hmatch = tp.hours is None or tp.hours.__contains__(t.hour)
            wdmatch = tp.weekdays is None or tp.weekdays.__contains__(t.weekday() + 1)
            dmatch = tp.days is None or tp.days.__contains__(t.day)
            momatch = tp.months is None or tp.months.__contains__(t.month)
            # print(f'time_period {str(tp)} matches: {mmatch and hmatch and wdmatch and dmatch and momatch}')
            if mmatch and hmatch and wdmatch and dmatch and momatch:
                if self.layout != tp:
                    self.logger.warning('switching layout from %s to %s', self.layout.layout, tp.layout)
                    self.check_pause_resume_job(self.layout.has_trains(), tp.has_trains(), TDF_JOB_ID)
                    self.check_pause_resume_job(self.layout.has_forecast(), tp.has_forecast(), WFF_JOB_ID)
                    self.check_pause_resume_job(self.layout.has_outdoor(), tp.has_outdoor(), CWF_JOB_ID)
                    self.check_pause_resume_job(self.layout.has_news(), tp.has_news(), NF_JOB_ID)
                    self.layout = tp
                    return

    def check_pause_resume_job(self, old, new, job_id):
        if old and not new:
            self.logger.warning('Pausing %s', {job_id})
            self.scheduler.pause_job(job_id)
        elif new and not old:
            self.logger.warning(f'Resuming %s', {job_id})
            self.scheduler.resume_job(job_id)
