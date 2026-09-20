import os

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


class Settings:
    """
    Central application configuration.

    All agents and services should access configuration
    through this class instead of reading environment
    variables directly.
    """

    # ============================================================
    # LLM CONFIGURATION
    # ============================================================

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant",
    )

    # Maximum number of iterations allowed inside an
    # agentic tool-use loop.
    MAX_AGENT_ITERATIONS: int = int(
        os.getenv("MAX_AGENT_ITERATIONS", "5")
    )

    RSS_FEEDS: dict[str, str] = {
        "Marketing Week": "https://www.marketingweek.com/feed/",
        "AdWeek": "https://www.adweek.com/feed/",
        "HubSpot Marketing": "https://blog.hubspot.com/marketing/rss.xml",
        "Content Marketing Institute": "https://contentmarketinginstitute.com/feed/",
        "MarTech": "https://martech.org/feed/",
        "The Guardian": "https://www.theguardian.com/business/technology/rss"
    }

    # ============================================================
    # NEWS API CONFIGURATION
    # ============================================================

    NEWSDATA_API_KEY: str = os.getenv(
        "NEWSDATA_API_KEY",
        ""
    )

    CURRENTS_API_KEY: str = os.getenv(
        "CURRENTS_API_KEY",
        ""
    )

    GNEWS_API_KEY: str = os.getenv(
        "GNEWS_API_KEY",
        ""
    )

    # ============================================================
    # ARTICLE PROCESSING
    # ============================================================

    MAX_ARTICLES: int = int(
        os.getenv("MAX_ARTICLES", "20")
    )

    MAX_RELEVANT_ARTICLES: int = int(
        os.getenv("MAX_RELEVANT_ARTICLES", "20")
    )

    ARTICLE_TIMEOUT_SECONDS: int = int(
        os.getenv("ARTICLE_TIMEOUT_SECONDS", "15")
    )

    # ============================================================
    # RAG CONFIGURATION
    # ============================================================

    RAG_TOP_K: int = int(
        os.getenv("RAG_TOP_K", "5")
    )

    KNOWLEDGE_BASE_PATH: str = os.getenv(
        "KNOWLEDGE_BASE_PATH",
        "data/knowledge_base",
    )

    MAX_LLM_RETRIES: int = int(
        os.getenv("MAX_LLM_RETRIES", "3")
    )

    LLM_RETRY_BASE_DELAY: float = float(
        os.getenv("LLM_RETRY_BASE_DELAY", "2")
    )

    # ============================================================
    # APPLICATION
    # ============================================================

    APP_NAME: str = "Marketing News Intelligence Agent"

    APP_VERSION: str = "1.0.0"


settings = Settings()