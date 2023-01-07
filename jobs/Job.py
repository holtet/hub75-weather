class AbstractJob:
    def job_id(self) -> str:
        pass

    def run(self):
        pass

    def interval(self) -> int:
        pass
