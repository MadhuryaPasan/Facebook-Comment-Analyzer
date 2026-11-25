"""Standalone Facebook Graph API client library.

This module is intentionally self-contained and MUST NOT import anything from
`app.*` (no FastAPI, SQLModel, or app config imports). It depends only on the
Python standard library and `httpx`, so it can be developed independently and
later extracted or packaged as a reusable library.

Usage example:
    from libs.facebook_graph import FacebookGraphClient

    with FacebookGraphClient(access_token="...", api_version="v21.0") as fb:
        posts = fb.get_page_posts(page_id="123456789")
        comments = fb.get_post_comments(post_id="123456789_987654321")
"""
