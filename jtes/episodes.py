import feedparser

from collections import namedtuple

from datetime import date


FEED_URL = 'http://www.jedentageinset.de/feed/'
Episode = namedtuple('Episode', ['path', 'name', 'published'])


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
