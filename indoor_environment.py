import logging
import time
import bme280
import smbus2
from apds9960.const import *
from apds9960 import APDS9960
from dto import *


class IndoorEnvironmentFetcher:
    PORT = 1  # i2c port
    ADDRESS = 0x76  # Adafruit BME280 address. Other BME280s may be different

    def __init__(self, collection: DataCollection):
        self.collection = collection
        self.logger = logging.getLogger(__name__)
        self.bus = smbus2.SMBus(self.PORT)
        calibrated = False
        while not calibrated:
            try:
                bme280.load_calibration_params(self.bus, self.ADDRESS)
                calibrated = True
            except Exception as e:
                self.logger.error('Failed to calibrate bme280: %s', str(e))
                time.sleep(5)
        self.apds = APDS9960(self.bus)
        self.apds.enableLightSensor()
        #        apds.enableGestureSensor()

    def run(self):
        if True:
            try:
                new_env_data = IndoorEnvironmentData()
                bme280_data = bme280.sample(self.bus, self.ADDRESS)
                new_env_data.humidity = bme280_data.humidity
                new_env_data.pressure = bme280_data.pressure
                new_env_data.temperature = bme280_data.temperature
                self.collection.indoor_environment_data = new_env_data
            except Exception as e:
                self.logger.error('Failed to fetch indoor environment: %s', str(e))
                raise Exception('Failed to fetch indoor environment')
            try:
                self.collection.ambient_light = self.apds.readAmbientLight()
                if False:
                    #                if apds.isGestureAvailable():
                    print(f"gesture available")
                    motion = self.apds.readGesture()
                    print(f"gesture code {motion}")
                    if (motion == APDS9960_DIR_UP):
                        new_env_data.time_offset += 15
                    elif (motion == APDS9960_DIR_DOWN):
                        new_env_data.time_offset -= 15
            except Exception as e:
                self.logger.error('Failed to fetch brightness: %s', str(e))
                raise Exception('Failed to fetch brightness')
