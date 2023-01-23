class Job:
    def __init__(self, job, interval_ok, interval_error):
        self.job = job
        self.last_success = True
        self.interval_ok = interval_ok
        self.interval_error = interval_error
