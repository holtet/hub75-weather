import twitter
import feedparser
from dto import *
from config import Config


class NewsFetcher:

    def __init__(self, collection: DataCollection, config1: Config):
        self.collection = collection
        self.config = config1
        self.api = twitter.Api("","","","")
        
    def run(self):
        try:
            print("Fetching news")
#            NewsFeed = feedparser.parse("https://www.nrk.no/toppsaker.rss")
#            newsFeed = feedparser.parse("https://www.nrk.no/osloogviken/toppsaker.rss")
            newsFeed = feedparser.parse("https://www.vg.no/rss/feed/?categories=1069%2C1070&limit=10&format=rss&private=1")

            for index, entry in enumerate(newsFeed.entries[:5]):
#                print(str(entry))
                self.collection.news_list[index] = NewsItem(f'{entry.title} - {entry.summary}')             
#                self.collection.news_list[index] = NewsItem(f'{entry.summary}')             
#            entry = NewsFeed.entries[1]

#            print (entry.published)
#            print ("******")
#            print (entry.summary)
#            print ("------News Link--------")
#            print (entry.link)

        except Exception as e:
            print(f'News fetcher failed: {str(e)}')
            raise e

    def twitter(self):
        try:
            print("Fetching news")
            statuses = self.api.GetUserTimeline(1217752287621320704)
            print([s.text for s in statuses])
        except Exception as e:
            print(f'News fetcher failed: {str(e)}')
            raise e
