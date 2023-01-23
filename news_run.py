import configparser

from dt.data_collection import DataCollection
from jobs.news import NewsFetcher
from config import Config

if __name__ == "__main__":
    collection = DataCollection()

    configp = configparser.ConfigParser()
    configp.read('../entur/config.ini')
    config = Config(configp)

    news = NewsFetcher(collection, config)
    news.run()

    for ne in collection.news_list:
        print(ne.text)
        
