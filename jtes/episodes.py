from datetime import date

import feedparser


class Episode(object):
    def __init__(self, path=None, name=None, published=None):
        self.path = path
        self.name = name
        self.published = published

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return 'Episode(path={}, name={}, published={})'.format(
            self.path, self.name, self.published
        )


FEED_URL = 'http://www.jedentageinset.de/feed/'


def available():
    feed = feedparser.parse(FEED_URL)
    entries = feed.entries
    return [
        Episode(
            path=entry.link, name=entry.title,
            published=date(
                year=entry.published_parsed.tm_year,
                month=entry.published_parsed.tm_mon,
                day=entry.published_parsed.tm_mday
            )
        )
        for entry in entries
    ]
