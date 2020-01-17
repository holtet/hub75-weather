import logging


class Listener:
    def __init__(self, joblist):
        self.joblist = joblist
        self.logger = logging.getLogger("Listener")

    def job_done_listener(self, event):
        job = self.joblist[event.job_id]
        if event.exception:
            self.logger.info('The job %s crashed', {event.job_id})
            if job.last_success:
                job.job.reschedule(trigger='interval', seconds=job.interval_error)
                job.last_success = False
        else:
            self.logger.info('The job %s was successful', {event.job_id})
            if not job.last_success:
                job.job.reschedule(trigger='interval', seconds=job.interval_ok)
                job.last_success = True
