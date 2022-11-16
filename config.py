import re
from dto import TimePeriod

class Config:
    def __init__(self, config):
        self.datetime_format = config["MAIN"].get("datetime_format", "%d/%m  %H:%M:%S")
        self.width = 128
        self.zs_width = self.width-1
        self.height = 64
        self.zs_height = self.height - 1

        self.weather_api_key = config["WEATHER"]["apiKey"]
        self.weather_city_id = config["WEATHER"]["cityId"]

        self.entur_client_id = config["TRAINS"]["clientId"]
        self.destinations = config["TRAINS"]["destinations"].split(",")
        self.stop_id = config["TRAINS"]["stopId"]
        self.max_train_departures = config["TRAINS"].get("maxTrainDepartures", 8)

        self.time_periods = []
        self.range_re = re.compile(r"\d+-\d+")

        for layout_name in list(filter(lambda x: str(x).startswith("SCREEN_"), config.sections())):
            print(f'found layout config {layout_name}')
            times = list(map(int, str(config[layout_name]["times"]).split(",")))
            for l in str(config[layout_name]["active"]).split("\n"):
                time_period = TimePeriod(layout_name, times)
                p = l.split(" ")
                time_period.minutes = self.conf_to_array(str(p[0]))
                time_period.hours = self.conf_to_array(str(p[1]))
                time_period.weekdays = self.conf_to_array(str(p[2]))
                time_period.days = self.conf_to_array(str(p[3]))
                time_period.months = self.conf_to_array(str(p[4]))
                self.time_periods.append(time_period)

    def conf_to_array(self, conf_str):
        if conf_str == "*":
            return None
        items = []
        mparts = conf_str.split(",")
        for mpart in mparts:
            if self.range_re.match(mpart):
                first_last = list(map(int, mpart.split("-")))
                for i in range(int(first_last[0]), int(first_last[1]) + 1):  # TODO: simplify
                    items.append(i)
            else:
                items.append(int(mpart))
        return items
