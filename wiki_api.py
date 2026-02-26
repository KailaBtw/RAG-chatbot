import json
import time
from typing import Dict, Iterable, List, Optional

import requests


class MediaWikiClient:
    """
    Minimal MediaWiki API client tailored for RuneScape Wiki.

    Provides methods to fetch the most viewed pages and retrieve page content.
    Includes basic retry logic and polite defaults (User-Agent, small delay).
    """

    def __init__(
        self,
        base_url: str = "https://runescape.wiki/api.php",
        session: Optional[requests.Session] = None,
        user_agent: str = (
            "GenreAnalysisBot/0.1 (student project; contact: example@example.com)"
        ),
        request_delay_seconds: float = 0.1,
        max_retries: int = 3,
        timeout_seconds: int = 20,
    ) -> None:
        self.base_url = base_url
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.request_delay_seconds = request_delay_seconds
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds

    def _request(self, params: Dict[str, str]) -> Dict:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(
                    self.base_url, params=params, timeout=self.timeout_seconds
                )
                response.raise_for_status()
                data = response.json()
                if "error" in data:
                    raise requests.HTTPError(str(data["error"]))
                return data
            except Exception as exc:  # noqa: BLE001 - intentional broad catch for retries
                last_exc = exc
                # Handle rate limiting with longer delays
                if "429" in str(exc) or "Too Many Requests" in str(exc):
                    sleep_for = 30 * attempt  # 30, 60, 90 seconds for rate limits
                    print(f"[genre-analysis] Rate limited, waiting {sleep_for}s...")
                else:
                    # Exponential backoff with floor on first delay
                    sleep_for = max(self.request_delay_seconds, 0.1) * (2 ** (attempt - 1))
                time.sleep(sleep_for)
        assert last_exc is not None
        raise last_exc

    def get_most_viewed_titles(self, limit: int = 100) -> List[str]:
        """
        Return titles of the most viewed pages.

        Uses MediaWiki list=mostviewed.
        The parameter name for limit is "pvimlimit" (pageviews-mostviewed limit).
        """
        # Clamp limit to a reasonable boundary for this project
        limit = max(1, min(limit, 500))
        params = {
            "action": "query",
            "format": "json",
            "list": "mostviewed",
            "pvimlimit": str(limit),
        }
        data = self._request(params)
        items = data.get("query", {}).get("mostviewed", [])
        titles: List[str] = []
        for item in items:
            title = item.get("title")
            if isinstance(title, str):
                titles.append(title)
        return titles

    def get_random_titles(self, limit: int = 10, namespace: int = 0) -> List[str]:
        """
        Return random page titles via list=random.
        namespace=0 restricts to main/article namespace by default.
        """
        limit = max(1, min(limit, 500))
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnlimit": str(limit),
            "rnnamespace": str(namespace),
        }
        data = self._request(params)
        items = data.get("query", {}).get("random", [])
        titles: List[str] = []
        for item in items:
            title = item.get("title")
            if isinstance(title, str):
                titles.append(title)
        return titles

    def get_random_titles_batch(self, total_limit: int = 500, batch_size: int = 500) -> List[str]:
        """
        Get random titles in a single batch to avoid API overload.
        Returns up to 500 unique titles (API limit).
        """
        # Limit to single batch to avoid overloading API
        actual_limit = min(total_limit, 500)
        
        print(f"[genre-analysis] Fetching {actual_limit} titles in single batch...")
        
        batch_titles = self.get_random_titles(limit=actual_limit)
        all_titles = set(batch_titles)  # Remove any duplicates
        
        print(f"[genre-analysis] Retrieved {len(all_titles)} unique titles")
        
        return list(all_titles)


    def get_page_wikitext(self, title: str) -> str:
        """
        Fetch raw wikitext for a given page title via action=parse&prop=wikitext.
        """
        params = {
            "action": "parse",
            "format": "json",
            "page": title,
            "prop": "wikitext",
        }
        data = self._request(params)
        return (
            data.get("parse", {})
            .get("wikitext", {})
            .get("*", "")
        )

    def get_pages_wikitext(self, titles: Iterable[str]) -> Dict[str, str]:
        """
        Convenience helper to fetch multiple pages' wikitext, serially with a tiny delay.
        """
        results: Dict[str, str] = {}
        for title in titles:
            results[title] = self.get_page_wikitext(title)
            time.sleep(self.request_delay_seconds)
        return results

    @staticmethod
    def write_jsonl(path: str, records: Iterable[Dict]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    @staticmethod
    def write_json(path: str, data: List[Dict]) -> None:
        """Write a UTF-8 JSON array to disk."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


