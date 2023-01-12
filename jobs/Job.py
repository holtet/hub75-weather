class AbstractJob:
    @staticmethod
    def job_id() -> str:
        pass

    def run(self):
        pass

    @staticmethod
    def interval() -> int:
        pass
