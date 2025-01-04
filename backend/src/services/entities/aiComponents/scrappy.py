from typing import Optional
from datetime import datetime, timedelta
import logging

import feedparser
import pytz
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

from src.constants import Status
from src.services.entities.plugin import BasePlugin, PluginJob

logger = logging.getLogger("oracle.app")

MODEL_ID = "kk08/CryptoBERT"
logger.info(f"Loading Model {MODEL_ID}...")
tokenizer = BertTokenizer.from_pretrained(MODEL_ID)
model = BertForSequenceClassification.from_pretrained(MODEL_ID)
classifier = pipeline("sentiment-analysis", model=MODEL_ID, tokenizer=tokenizer)


class Scrappy(BasePlugin):
    PluginJob = PluginJob.AFTER_EVALUATION

    def __init__(self, ticker_whitelist: Optional[list[str]] = None, keyword: Optional[list[str]] = None,
                 days_passed: Optional[int] = None, weight: int = 1, cache_days: float = 1, _last_cached: Optional[datetime] = None,
                 _cached_values: Optional[dict[str, dict[int, float]]] = None):
        """
        Scraps news from yfinance.

        :param ticker_whitelist: List of tickers to scrape news from.
        :param keyword: List of keywords to filter news by.
        :param days_passed: Number of days to go back in time.
        :param weight: Weight of the plugin.
        :param cache_days: Number of days to cache the results.
        :param _last_cached: Last time the results were cached.
        :param _cached_values: Cached results.
        """
        self.ticker_whitelist: Optional[list[str]] = ticker_whitelist
        self.keyword: Optional[list[str]] = keyword
        self.days_passed: Optional[int] = days_passed
        self.weight: int = weight

        self.cache_days: float = cache_days
        self.last_cached: Optional[datetime] = _last_cached
        self.cached_values: dict[str, float] = _cached_values if _cached_values is not None else {}

    def run(self, profile: 'Profile', tc_confidences: Optional[dict[str, dict[int, float]]] = None) -> dict[str, dict[int, float]]:
        if profile.status == Status.BACKTESTING:
            return tc_confidences

        if self.last_cached is None:
            self.last_cached = datetime.now(pytz.UTC)

        if self.last_cached + timedelta(days=self.cache_days) < datetime.now(pytz.UTC):
            self.last_cached = datetime.now(pytz.UTC)
            self.cached_values: dict[str, float] = {}

        for ticker in self.ticker_whitelist:
            if ticker not in tc_confidences:
                continue

            if ticker not in self.cached_values:
                self.cached_values[ticker] = self.sentiment_analysis(ticker)

            tc_confidences[ticker][len(tc_confidences[ticker])] = self.cached_values[ticker]

        return tc_confidences

    def sentiment_analysis(self, ticker) -> float:
        articles: list[str] = self.extract_yfinance_content(ticker)

        confidences: list[float] = []
        sentiments: list[dict[str, float | str]] = classifier(articles)

        for sentiment in sentiments:
            if sentiment["label"] == "LABEL_0":
                confidences.append(-sentiment["score"])
            else:
                confidences.append(sentiment["score"])

        average_confidence: float = sum(confidences) / len(confidences)

        return average_confidence

    def extract_yfinance_content(self, ticker: str) -> list[str]:
        date_limit: Optional[datetime] = None
        if self.days_passed is not None:
            date_limit = datetime.now(pytz.UTC) - timedelta(days=self.days_passed)

        rss_url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
        feed: feedparser = feedparser.parse(rss_url)

        articles: list[str] = []

        for i, entry in enumerate(feed.entries):
            if self.keyword is not None and not any(kw.lower() in entry.title.lower() for kw in self.keyword):
                continue

            if date_limit is not None and date_limit > datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z"):
                print("Date limit reached")
                continue

            print(f"Title: {entry.title}")
            print(f"Link: {entry.link}")
            print(f"Published: {entry.published}")
            print(f"Summary: {entry.summary}")

            print("=" * 50)

            articles.append(entry.title + entry.summary)

        return articles
