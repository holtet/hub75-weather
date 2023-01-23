from dt.scroll_text import ScrollText


class NewsItem:
    def __init__(self, text):
        self.text = ScrollText(text, 0, 128, 128)
