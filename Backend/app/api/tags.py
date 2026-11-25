OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "health",
        "description": "Service liveness and readiness checks.",
    },
    {
        "name": "posts",
        "description": "Browse ingested Facebook Page posts, comment totals, and sentiment summaries.",
    },
    {
        "name": "comments",
        "description": "Search and inspect Facebook comments, replies, and NLP analysis details.",
    },
    {
        "name": "analysis",
        "description": "Trigger and track asynchronous Graph API ingestion and comment analysis jobs.",
    },
]
