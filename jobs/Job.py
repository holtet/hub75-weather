class AbstractJob:
    @staticmethod
    def job_id() -> str:
        pass

    def run(self):
        pass

    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600
