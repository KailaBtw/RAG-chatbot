import json
from pathlib import Path
from typing import Any, Dict

import requests

from Applications.Genre_Analysis.wiki_api import MediaWikiClient


class DummyResponse:
    def __init__(self, payload: Dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")

    def json(self) -> Dict[str, Any]:
        return self._payload


class DummySession:
    def __init__(self) -> None:
        self.headers = {}
        self.calls = []

    def get(self, url: str, params: Dict[str, str], timeout: int):
        self.calls.append((url, params))
        if params.get("list") == "mostviewed":
            items = [
                {"title": f"Page {i+1}", "count": 1000 - i}
                for i in range(int(params.get("pvimlimit", "10")))
            ]
            return DummyResponse({"query": {"mostviewed": items}})
        if params.get("list") == "random":
            items = [
                {"id": i + 1, "ns": 0, "title": f"Random Page {i+1}"}
                for i in range(int(params.get("rnlimit", "10")))
            ]
            return DummyResponse({"query": {"random": items}})
        if params.get("action") == "parse":
            title = params.get("page", "")
            return DummyResponse({"parse": {"wikitext": {"*": f"Wikitext of {title}"}}})
        return DummyResponse({}, status_code=404)


def test_get_most_viewed_titles_and_wikitext(tmp_path: Path) -> None:
    session = DummySession()
    client = MediaWikiClient(session=session)

    titles = client.get_most_viewed_titles(limit=5)
    assert len(titles) == 5
    assert titles[0] == "Page 1"

    pages = client.get_pages_wikitext(titles)
    assert pages["Page 1"] == "Wikitext of Page 1"

    out_file = tmp_path / "out.json"
    client.write_json(str(out_file), [
        {"title": t, "wikitext": pages[t]} for t in titles
    ])
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) == 5
    assert data[0]["title"] == "Page 1"
    assert data[0]["wikitext"] == "Wikitext of Page 1"



def test_limit_is_clamped_and_param_stringified() -> None:
    session = DummySession()
    client = MediaWikiClient(session=session)

    titles = client.get_most_viewed_titles(limit=9999)
    # Should clamp to 500 according to implementation
    assert len(titles) == 500
    # Last recorded call should include pvimlimit as string "500"
    _, params = session.calls[-1]
    assert params.get("pvimlimit") == "500"


def test_user_agent_header_is_set() -> None:
    session = DummySession()
    ua = "UnitTestAgent/1.0"
    _ = MediaWikiClient(session=session, user_agent=ua)
    assert session.headers.get("User-Agent") == ua


def test_write_jsonl(tmp_path: Path) -> None:
    client = MediaWikiClient(session=DummySession())
    out_file = tmp_path / "out.jsonl"
    records = [{"a": 1}, {"b": 2}]
    client.write_jsonl(str(out_file), records)
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert parsed[0] == {"a": 1} and parsed[1] == {"b": 2}


def test_error_response_raises_http_error() -> None:
    class ErrSession(DummySession):
        def get(self, url, params, timeout):
            # Simulate a well-formed 200 with MediaWiki "error" payload
            return DummyResponse({"error": {"code": "badrequest", "info": "oops"}}, 200)

    client = MediaWikiClient(session=ErrSession())
    import pytest

    with pytest.raises(requests.HTTPError):
        client.get_most_viewed_titles(limit=1)


def test_retry_then_success(monkeypatch) -> None:
    # Simulate first call failing with HTTP 500 then succeeding
    class FlakySession(DummySession):
        def __init__(self) -> None:
            super().__init__()
            self._count = 0

        def get(self, url, params, timeout):
            self._count += 1
            if self._count == 1:
                return DummyResponse({}, status_code=500)
            # On retry, return a minimal valid mostviewed payload
            return DummyResponse({"query": {"mostviewed": [{"title": "X"}]}})

    # Avoid actual sleeping to speed up the test
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    client = MediaWikiClient(session=FlakySession(), max_retries=2, request_delay_seconds=0)
    titles = client.get_most_viewed_titles(limit=1)
    assert titles == ["X"]
def test_get_random_titles() -> None:
    session = DummySession()
    client = MediaWikiClient(session=session)
    titles = client.get_random_titles(limit=3)
    assert titles == ["Random Page 1", "Random Page 2", "Random Page 3"]



def test_zero_random_results_returns_empty_list() -> None:
    class EmptySession(DummySession):
        def get(self, url, params, timeout):
            return DummyResponse({"query": {"random": []}})

    client = MediaWikiClient(session=EmptySession())
    titles = client.get_random_titles(limit=5)
    assert titles == []