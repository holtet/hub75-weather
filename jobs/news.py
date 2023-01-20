import twitter
import feedparser
from dto import *
from config import Config
from jobs.Job import AbstractJob
from jobs.jobexception import JobException


class NewsFetcher(AbstractJob):
    @staticmethod
    def interval() -> int:
        return 3600

    @staticmethod
    def retry_interval() -> int:
        return 600

    @staticmethod
    def job_id():
        return 'news_job_id'

    def __init__(self, collection: DataCollection, config: Config):
        self.collection = collection
        self.config = config

    def run(self):
        try:
            #            NewsFeed = feedparser.parse("https://www.nrk.no/toppsaker.rss")
            #            news_feed = feedparser.parse("https://www.nrk.no/osloogviken/toppsaker.rss")
            news_feed = feedparser.parse(self.config.news_url)

            for index, entry in enumerate(news_feed.entries[:8]):
                self.collection.news_list[index] = NewsItem(f'{entry.title} - {entry.summary}')

        except Exception as e:
            raise JobException(f'News fetcher failed: {str(e)}')
