from datetime import datetime
from typing import List

import feedparser

from app.config.settings import settings
from app.models.article import Article


class RSSFeedError(Exception):
    """Raised when an RSS feed cannot be processed."""


class RSSTool:
    """
    Collects and normalizes articles from configured RSS feeds.

    Responsibility:
        RSS feeds → normalized Article objects

    This tool does NOT perform LLM reasoning.
    """

    def __init__(self) -> None:
        self.feeds = settings.RSS_FEEDS

    def fetch_feed(
        self,
        source: str,
        url: str,
    ) -> List[Article]:
        """
        Fetch and normalize articles from a single RSS feed.
        """

        try:
            feed = feedparser.parse(url)

            # feedparser may not raise an exception for malformed feeds,
            # so explicitly check whether parsing succeeded.
            if getattr(feed, "bozo", False) and not feed.entries:
                raise RSSFeedError(
                    f"Failed to parse RSS feed: {source}"
                )

            articles: List[Article] = []

            for entry in feed.entries:

                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if not title or not link:
                    continue

                description = entry.get(
                    "summary",
                    entry.get("description", ""),
                )

                published_at = self._parse_date(entry)

                author = entry.get("author")

                article = Article(
                    title=title,
                    url=link,
                    source=source,
                    description=description,
                    published_at=published_at,
                    author=author,
                )

                articles.append(article)

            return articles

        except RSSFeedError:
            raise

        except Exception as exc:
            raise RSSFeedError(
                f"Unexpected error while fetching {source}: {exc}"
            ) from exc

    def fetch_all(self) -> List[Article]:
        """
        Fetch articles from all configured RSS feeds.

        A failure in one source does not stop the entire
        ingestion process.
        """

        all_articles: List[Article] = []

        for source, url in self.feeds.items():

            try:
                articles = self.fetch_feed(
                    source=source,
                    url=url,
                )

                all_articles.extend(articles)

                print(
                    f"[RSS] {source}: "
                    f"{len(articles)} articles collected"
                )

            except RSSFeedError as exc:

                print(
                    f"[RSS ERROR] {source}: {exc}"
                )

                # Continue processing other sources.
                continue

        return all_articles

    @staticmethod
    def _parse_date(entry) -> datetime | None:
        """
        Convert RSS published/updated metadata into datetime.
        """

        parsed_time = entry.get(
            "published_parsed",
            entry.get("updated_parsed"),
        )

        if parsed_time is None:
            return None

        try:
            return datetime(
                parsed_time.tm_year,
                parsed_time.tm_mon,
                parsed_time.tm_mday,
                parsed_time.tm_hour,
                parsed_time.tm_min,
                parsed_time.tm_sec,
            )
        except (AttributeError, ValueError):
            return None


rss_tool = RSSTool()