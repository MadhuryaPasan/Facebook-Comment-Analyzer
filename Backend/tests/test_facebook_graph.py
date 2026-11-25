import ast
from pathlib import Path

import httpx
import pytest

from app.pipeline.fetcher import FacebookCommentFetcher
from libs.facebook_graph import (
    FacebookGraphAuthError,
    FacebookGraphClient,
    FacebookGraphNotFoundError,
    FacebookGraphRateLimitError,
)


def test_facebook_graph_is_standalone_single_file_library() -> None:
    """Verify `libs/facebook_graph.py` never imports from `app.*`."""
    source_path = Path(__file__).resolve().parents[1] / "libs" / "facebook_graph.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))

    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)

    assert not any(
        mod == "app" or mod.startswith("app.") for mod in imported_modules
    ), f"libs/facebook_graph.py must stay independent of app.*, found: {imported_modules}"


def test_facebook_graph_client_fetches_paginated_comments() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["access_token"] == "test-token"
        if request.url.params.get("after") == "cursor-2":
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "c_2",
                            "message": "Fast delivery",
                            "created_time": "2026-11-25T09:05:00+0000",
                            "like_count": 3,
                            "from": {"id": "user_2"},
                        }
                    ]
                },
            )
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "c_1",
                        "message": "Great product",
                        "created_time": "2026-11-25T09:00:00+0000",
                        "like_count": 1,
                        "from": {"id": "user_1"},
                    }
                ],
                "paging": {"cursors": {"after": "cursor-2"}},
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(base_url="https://graph.facebook.com/v21.0", transport=transport) as http_client:
        fb = FacebookGraphClient(access_token="test-token", http_client=http_client)
        fetcher = FacebookCommentFetcher(fb)
        results = fetcher.fetch_post_comments("page_post_1")

    assert len(results) == 2
    assert results[0].comment_id == "c_1"
    assert results[1].comment_id == "c_2"
    assert results[0].author_hash != "user_1"
    assert results[0].author_hash is not None


@pytest.mark.parametrize(
    ("status_code", "error_code", "exc_cls"),
    [
        (401, 190, FacebookGraphAuthError),
        (429, 613, FacebookGraphRateLimitError),
        (404, 803, FacebookGraphNotFoundError),
    ],
)
def test_facebook_graph_client_maps_api_errors(
    status_code: int,
    error_code: int,
    exc_cls: type[Exception],
) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json={"error": {"message": "API error", "code": error_code}},
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(base_url="https://graph.facebook.com/v21.0", transport=transport) as http_client:
        fb = FacebookGraphClient(access_token="test-token", http_client=http_client)
        with pytest.raises(exc_cls):
            fb.get_page_posts("12345")
