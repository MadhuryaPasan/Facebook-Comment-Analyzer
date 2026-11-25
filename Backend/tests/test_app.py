from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_schema_includes_documented_routes_and_tags() -> None:
    schema = app.openapi()
    tag_names = {tag["name"]: tag["description"] for tag in schema.get("tags", [])}
    assert {"health", "posts", "comments", "analysis"} <= set(tag_names.keys())
    assert all(tag_names[name] for name in ("health", "posts", "comments", "analysis"))

    paths = schema.get("paths", {})
    expected_paths = {
        "/health",
        "/api/v1/posts",
        "/api/v1/posts/{post_id}",
        "/api/v1/posts/{post_id}/comments",
        "/api/v1/comments",
        "/api/v1/comments/{comment_id}",
        "/api/v1/comments/analyze",
    }
    assert expected_paths <= set(paths.keys())

    for path, operations in paths.items():
        for method, spec in operations.items():
            assert spec.get("summary"), f"Missing summary on {method.upper()} {path}"
            assert spec.get("description"), f"Missing description on {method.upper()} {path}"
