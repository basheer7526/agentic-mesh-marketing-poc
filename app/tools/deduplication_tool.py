import hashlib
import re
from typing import List

from app.models.article import Article


class DeduplicationTool:
    """
    Removes duplicate articles using normalized URLs
    and content fingerprints.

    Responsibility:
        Articles → unique articles

    This tool performs deterministic processing.
    It does not use an LLM.
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize a URL so tracking parameters don't cause
        the same article to appear as multiple articles.
        """

        url = url.strip().lower()

        # Remove common tracking parameters.
        url = re.sub(
            r"[?&](utm_[^&]+|fbclid|gclid)=[^&]+",
            "",
            url,
        )

        # Remove trailing slash.
        url = url.rstrip("/")

        return url

    @staticmethod
    def create_content_hash(article: Article) -> str:
        """
        Create a deterministic fingerprint using article
        title and description.
        """

        title = article.title.strip().lower()

        description = (
            article.description or ""
        ).strip().lower()

        content = f"{title}|{description}"

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

    def deduplicate(
        self,
        articles: List[Article],
    ) -> List[Article]:
        """
        Remove duplicate articles.

        Primary key:
            normalized URL

        Secondary key:
            title + description hash
        """

        unique_articles: List[Article] = []

        seen_urls: set[str] = set()
        seen_hashes: set[str] = set()

        for article in articles:

            normalized_url = self.normalize_url(
                article.url
            )

            content_hash = self.create_content_hash(
                article
            )

            # Store the fingerprint on the article.
            article.url = normalized_url
            article.content_hash = content_hash

            # Duplicate URL.
            if normalized_url in seen_urls:
                continue

            # Duplicate content.
            if content_hash in seen_hashes:
                continue

            seen_urls.add(normalized_url)
            seen_hashes.add(content_hash)

            unique_articles.append(article)

        return unique_articles


deduplication_tool = DeduplicationTool()