from __future__ import annotations
import logging
import os
import random
import time

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Generator, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


DEFAULT_API_VERSION = "v27.0"
DEFAULT_BASE_URL = "https://graph.facebook.com"

DEFAULT_TIMEOUT = (5, 30)  # Connection/read timeout

DEFAULT_MAX_RETRIES = 4  # Maximum retries per request
DEFAULT_BACKOFF_FACTOR = 2.0  # Exponential backoff base
DEFAULT_MAX_BACKOFF = 60.0  # Maximum retry delay

RETRYABLE_HTTP_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}

RETRYABLE_GRAPH_ERROR_CODES = {
    1,  # Unknown API error
    2,  # Temporary API service error
}

# Meta rate-limit errors.
# These should normally stop automatic requests rather than repeatedly retrying and increasing API usage.
RATE_LIMIT_ERROR_CODES = {
    4,
    17,
    32,
    341,
    613,
    80001,
}

# used to track Meta Graph API usage
USAGE_HEADERS = (
    "X-App-Usage",  # Shows API usage against app's limits.
    "X-Page-Usage",  # Shows API usage associated with a Facebook Page.
    "X-Business-Use-Case-Usage",  # Shows usage for business-related API use cases.
)


class MetaGraphAPIError(Exception):
    """Structured exception for Meta Graph API failures."""

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[int] = None,
        error_subcode: Optional[int] = None,
        http_status: Optional[int] = None,
        error_type: Optional[str] = None,
        fbtrace_id: Optional[str] = None,
        is_transient: bool = False,
    ):
        """
        Initialize a structured Meta Graph API error.

        message:
            Human-readable error description.

        error_code:
            Graph API error code, if returned by Meta.

        error_subcode:
            Graph API error subcode, if returned by Meta.

        http_status:
            HTTP status code from the response, if available.

        error_type:
            Graph API error type string, if provided.

        fbtrace_id:
            Meta trace ID for debugging requests with support or logs.

        is_transient:
            Whether the failure appears temporary and eligible for retry.
        """

        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.error_subcode = error_subcode
        self.http_status = http_status
        self.error_type = error_type
        self.fbtrace_id = fbtrace_id
        self.is_transient = is_transient

    def __str__(self) -> str:
        details = []

        if self.error_code is not None:
            details.append(f"code={self.error_code}")

        if self.error_subcode is not None:
            details.append(f"subcode={self.error_subcode}")

        if self.http_status is not None:
            details.append(f"http_status={self.http_status}")

        suffix = f" ({', '.join(details)})" if details else ""

        return f"{self.message}{suffix}"


# Main Client for Meta Graph API
class FacebookCommentAnalyzerClient:
    """
    Client for interacting with the Meta Graph API.

    Features:
        - Access token authentication
        - Persistent HTTP connection pooling
        - Configurable connection/read timeouts
        - Bounded retries with exponential backoff and jitter
        - Retry-After support
        - Structured Graph API errors
        - Cursor-based pagination
        - Configurable page size and total result limits
        - Pagination URL validation
        - Usage header monitoring
        - Context manager support

    Environment variables:
        FACEBOOK_ACCESS_TOKEN
        PAGE_ID
    """

    BASE_URL = DEFAULT_BASE_URL

    def __init__(
        self,
        access_token: Optional[str] = None,
        api_version: str = DEFAULT_API_VERSION,
        timeout: Union[int, Tuple[float, float]] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        max_backoff: float = DEFAULT_MAX_BACKOFF,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        user_agent: str = "FacebookCommentAnalyzer/1.0",
        retry_rate_limit_errors: bool = False,
    ):
        """
        Initialize the Graph API client, validate configuration, and create an HTTP session.

        access_token:
            Explicit Facebook access token.
            None falls back to FACEBOOK_ACCESS_TOKEN in the environment.

        api_version:
            Graph API version string in "vMAJOR.MINOR" format (for example, "v27.0").

        timeout:
            Request timeout in seconds as a single positive number or a
            (connect_timeout, read_timeout) tuple.

        max_retries:
            Maximum retry attempts after the initial request fails.
            0 disables retries.

        backoff_factor:
            Multiplier used for exponential backoff between retry attempts.

        max_backoff:
            Upper cap in seconds for any single retry delay.

        pool_connections:
            Number of connection pools to cache in the HTTPS adapter.

        pool_maxsize:
            Maximum number of connections to save per pool.

        user_agent:
            Value sent in the User-Agent request header.

        retry_rate_limit_errors:
            Whether to retry rate-limit error codes automatically.
            False stops immediately on rate-limit errors to avoid extra quota usage.
        """
        # Authentication
        self._explicit_access_token = access_token
        resolved_token = self._get_access_token()

        if not resolved_token or not resolved_token.strip():
            raise ValueError(
                "No Facebook access token provided. "
                "Set FACEBOOK_ACCESS_TOKEN in your environment."
            )
        # configure validation
        if not isinstance(api_version, str) or not api_version.startswith("v"):
            raise ValueError("Invalid Graph API version.")

        version_number = api_version[1:].split(".")

        if len(version_number) != 2 or not all(
            part.isdigit() for part in version_number
        ):
            raise ValueError("Invalid Graph API version format.")

        if isinstance(timeout, (int, float)):
            timeout = (timeout, timeout)

        if (
            not isinstance(timeout, tuple)
            or len(timeout) != 2
            or any(
                not isinstance(value, (int, float)) or value <= 0 for value in timeout
            )
        ):
            raise ValueError(
                "timeout must be a positive number or "
                "a (connect_timeout, read_timeout) tuple."
            )

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        if backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative.")

        if max_backoff <= 0:
            raise ValueError("max_backoff must be positive.")

        if pool_connections < 1 or pool_maxsize < 1:
            raise ValueError("Connection pool sizes must be positive.")

        self.api_version = api_version
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.retry_rate_limit_errors = retry_rate_limit_errors

        # HTTP Session

        self.session = requests.Session()

        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=0,
        )

        self.session.mount("https://", adapter)

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": user_agent,
            }
        )

        self._closed = False

    def _get_access_token(self) -> Optional[str]:
        """
        Resolve the active Facebook access token.

        Returns the explicit token passed to __init__ if set, otherwise reads
        FACEBOOK_ACCESS_TOKEN from the environment.
        """
        return self._explicit_access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")

    # Resource Management
    def close(self) -> None:
        """
        Close the underlying HTTP session and mark the client as closed.

        Safe to call more than once.
        """

        if not self._closed:
            self.session.close()
            self._closed = True

    def __enter__(self):
        """
        Enter the context manager and return this client instance.

        Raises RuntimeError if the client has already been closed.
        """
        if self._closed:
            raise RuntimeError("The client has already been closed.")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # Validation
    @staticmethod
    def _validate_object_id(object_id: str, name: str) -> str:
        """
        Validate and clean a Graph API object ID or single path segment.

        object_id:
            Raw object ID or segment string to check.

        name:
            Label used in ValueError messages (for example, "post_id" or "page_id").
        """

        if not isinstance(object_id, str):
            raise ValueError(f"{name} must be a string.")

        object_id = object_id.strip()

        if (
            not object_id
            or "/" in object_id
            or "?" in object_id
            or "#" in object_id
            or any(char.isspace() for char in object_id)
        ):
            raise ValueError(f"Invalid {name}.")

        return object_id

    @staticmethod
    def _validate_message(message: str) -> str:
        """
        Validate and clean a Facebook comment or reply message.

        Allows special characters such as:
            / ? # @ ! & % + =

        Rejects empty or whitespace-only messages.
        """

        if not isinstance(message, str):
            raise ValueError("message must be a string.")

        message = message.strip()

        if not message:
            raise ValueError("message cannot be empty.")

        return message

    @staticmethod
    def _validate_fields(fields: str) -> str:
        """
        Validate and trim a Graph API `fields` query parameter.

        fields:
            Comma-separated field selection string.
        """

        if not isinstance(fields, str) or not fields.strip():
            raise ValueError("fields must be a non-empty string.")

        return fields.strip()

    def _build_url(self, endpoint: str) -> str:
        """
        Build a full versioned Graph API URL from a relative endpoint path.

        endpoint:
            Slash-separated Graph API path (for example, "{post_id}" or "{page_id}/posts").
        """

        if not isinstance(endpoint, str) or not endpoint:
            raise ValueError("Endpoint must be a non-empty string.")

        segments = endpoint.split("/")

        if any(not segment for segment in segments):
            raise ValueError("Invalid Graph API endpoint.")

        validated_segments = [
            self._validate_object_id(segment, "endpoint segment")
            for segment in segments
        ]

        return f"{self.BASE_URL}/{self.api_version}/{'/'.join(validated_segments)}"

    def _validate_pagination_url(self, url: str) -> None:
        """
        Validate a pagination URL returned by Meta against the configured base URL and API version.

        url:
            Full pagination URL (such as `paging.next`) to inspect before requesting.
        """

        try:
            base_parsed = urlparse(self.BASE_URL)
            parsed = urlparse(url)

            valid = (
                parsed.scheme == base_parsed.scheme
                and parsed.hostname == base_parsed.hostname
                and parsed.port == base_parsed.port
                and parsed.username is None
                and parsed.password is None
                and not parsed.fragment
                and parsed.path.startswith(f"/{self.api_version}/")
            )
        except (TypeError, ValueError):
            valid = False

        if not valid:
            raise MetaGraphAPIError("Rejected an invalid or untrusted pagination URL.")

    # Response parsing
    def _parse_response(
        self,
        response: requests.Response,
    ) -> Dict[str, Any]:
        """
        Decode a Graph API response and raise MetaGraphAPIError on JSON, Graph, or HTTP failures.

        response:
            HTTP response object returned by `requests.Session.request`.
        """

        try:
            data = response.json()

        except ValueError as exc:
            status = response.status_code

            raise MetaGraphAPIError(
                "Meta returned an invalid JSON response.",
                http_status=status,
                is_transient=(status in RETRYABLE_HTTP_STATUS_CODES or status >= 500),
            ) from exc

        if not isinstance(data, dict):
            raise MetaGraphAPIError(
                "Unexpected Graph API response format.",
                http_status=response.status_code,
            )

        # Graph API errors
        if "error" in data:

            error = data["error"]

            if not isinstance(error, dict):
                raise MetaGraphAPIError(
                    "Meta returned an invalid error payload.",
                    http_status=response.status_code,
                )

            code = error.get("code")
            subcode = error.get("error_subcode")

            is_rate_limit = code in RATE_LIMIT_ERROR_CODES

            is_transient = (
                code in RETRYABLE_GRAPH_ERROR_CODES
                or response.status_code in RETRYABLE_HTTP_STATUS_CODES
                or response.status_code >= 500
                or (bool(error.get("is_transient")) and not is_rate_limit)
            )

            raise MetaGraphAPIError(
                error.get("message", "Unknown Graph API error"),
                error_code=code,
                error_subcode=subcode,
                http_status=response.status_code,
                error_type=error.get("type"),
                fbtrace_id=error.get("fbtrace_id"),
                is_transient=is_transient,
            )

        # HTTP errors
        if not 200 <= response.status_code < 300:

            raise MetaGraphAPIError(
                f"HTTP request failed with status {response.status_code}.",
                http_status=response.status_code,
                is_transient=(
                    response.status_code in RETRYABLE_HTTP_STATUS_CODES
                    or response.status_code >= 500
                ),
            )

        return data

    # Usage Monitoring
    @staticmethod
    def _log_usage_headers(
        response: requests.Response,
    ) -> None:
        """
        Log Meta quota and usage headers when present on a response.

        response:
            HTTP response object containing headers from Meta.
        """

        for header in USAGE_HEADERS:

            usage = response.headers.get(header)

            if usage:
                logger.info(
                    "Meta API usage [%s]: %s",
                    header,
                    usage,
                )

    # Retry handling
    def _get_retry_delay(
        self,
        attempt: int,
        response: Optional[requests.Response] = None,
    ) -> float:
        """
        Compute how long to wait before the next retry attempt.

        attempt:
            Zero-based retry index for the failed attempt.

        response:
            Optional HTTP response used to check for a `Retry-After` header.
        """

        if response is not None:

            retry_after = response.headers.get("Retry-After")

            if retry_after:

                try:
                    delay = float(retry_after)

                except ValueError:

                    try:
                        retry_date = parsedate_to_datetime(retry_after)

                        if retry_date.tzinfo is None:
                            retry_date = retry_date.replace(tzinfo=timezone.utc)

                        delay = (
                            retry_date - datetime.now(timezone.utc)
                        ).total_seconds()

                    except (TypeError, ValueError, OverflowError):
                        delay = -1

                if delay >= 0:
                    return min(delay, self.max_backoff)

        exponential_delay = self.backoff_factor * (2**attempt)

        exponential_delay = min(
            exponential_delay,
            self.max_backoff,
        )

        return random.uniform(0, exponential_delay)

    def _should_retry(
        self,
        error: MetaGraphAPIError,
        attempt: int,
    ) -> bool:
        """
        Decide whether a `MetaGraphAPIError` should trigger another attempt.

        error:
            Parsed exception raised from the failed response.

        attempt:
            Zero-based retry index for the failed attempt.
        """

        if attempt >= self.max_retries:
            return False

        if error.error_code in RATE_LIMIT_ERROR_CODES:
            return self.retry_rate_limit_errors

        return error.is_transient

    # Core Request handler
    def _request_url(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        include_access_token: bool = True,
        allow_retry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Send an HTTP request to a full URL with bounded retries for retryable failures.

        url:
            Target URL to request.

        method:
            HTTP verb such as "GET", "POST", "PUT", or "DELETE".

        params:
            Optional query string parameters.

        json_data:
            Optional JSON-encoded request body.

        data:
            Optional form-encoded request body.

        include_access_token:
            Whether to attach the client's `access_token` query parameter.
            Set to False for pre-signed pagination URLs that already include it.

        allow_retry:
            Override whether retries are permitted.
            None retries only idempotent "GET" and "DELETE" requests by default.
        """
        if self._closed:
            raise RuntimeError("The client is closed.")

        http_method = method.upper()
        request_params = dict(params or {})

        if include_access_token:
            token = self._get_access_token()
            if not token or not token.strip():
                raise ValueError(
                    "No Facebook access token provided. "
                    "Set FACEBOOK_ACCESS_TOKEN in your environment."
                )
            request_params["access_token"] = token

        # Only retry idempotent methods by default to avoid duplicate writes.
        can_retry = (
            (http_method in {"GET", "DELETE"}) if allow_retry is None else allow_retry
        )

        for attempt in range(self.max_retries + 1):
            response = None
            try:
                response = self.session.request(
                    method=http_method,
                    url=url,
                    params=request_params or None,
                    json=json_data,
                    data=data,
                    timeout=self.timeout,
                    allow_redirects=False,
                )

                self._log_usage_headers(response)
                return self._parse_response(response)

            except MetaGraphAPIError as exc:
                if not can_retry or not self._should_retry(exc, attempt):
                    logger.error("Meta API request failed: %s", exc)
                    raise

                delay = self._get_retry_delay(attempt, response)
                logger.warning(
                    "Temporary API failure. Retry %d/%d in %.2f seconds.",
                    attempt + 1,
                    self.max_retries,
                    delay,
                )
                time.sleep(delay)

            except requests.exceptions.RequestException as exc:
                if not can_retry or attempt >= self.max_retries:
                    logger.error(
                        "Meta API network failure: %s",
                        type(exc).__name__,
                    )
                    raise MetaGraphAPIError(
                        "Network error communicating with Meta API.",
                        is_transient=True,
                    ) from exc

                delay = self._get_retry_delay(attempt, response)
                logger.warning(
                    "Network failure. Retry %d/%d in %.2f seconds.",
                    attempt + 1,
                    self.max_retries,
                    delay,
                )
                time.sleep(delay)

            finally:
                if response is not None:
                    response.close()

        raise RuntimeError("Unexpected request termination.")

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        allow_retry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Send a request to a relative Graph API endpoint.

        endpoint:
            Relative Graph API path (for example, "{post_id}" or "{page_id}/posts").

        method:
            HTTP verb such as "GET", "POST", "PUT", or "DELETE".

        params:
            Optional query string parameters.

        json_data:
            Optional JSON-encoded request body.

        data:
            Optional form-encoded request body.

        allow_retry:
            Override whether retries are permitted.
            None retries only idempotent "GET" and "DELETE" requests by default.
        """
        return self._request_url(
            self._build_url(endpoint),
            method=method,
            params=params,
            json_data=json_data,
            data=data,
            allow_retry=allow_retry,
        )

    # Paginating URL handling
    def _fetch_raw_url(self, url: str) -> Dict[str, Any]:
        """
        Validate and fetch a full pagination URL returned by Meta.

        url:
            Full URL from `paging.next`, which already contains cursor, limit, and token parameters.
        """

        self._validate_pagination_url(url)
        return self._request_url(
            url,
            include_access_token=False,
        )

    # generic pagination engine
    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_results: Optional[int] = None,
        max_pages: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Iterate through paginated items from a Graph API collection endpoint.

        endpoint:
            Relative Graph API collection path (for example, "{page_id}/posts").

        params:
            Initial query parameters for the first page request.

        max_results:
            Maximum total objects to yield across all pages.
            None yields all available items.

        max_pages:
            Maximum number of API pages to fetch.
            None fetches until no `paging.next` URL remains.

        Yields:
            Individual item dictionaries from each page's `data` list.
        """
        if max_results is not None and max_results < 0:
            raise ValueError("max_results cannot be negative.")

        if max_pages is not None and max_pages < 1:
            raise ValueError("max_pages must be positive.")

        if max_results == 0:
            return

        next_url = None
        current_params = dict(params or {})

        yielded_count = 0
        page_count = 0

        visited_urls = set()

        while True:

            if self._closed:
                raise RuntimeError("The client is closed.")

            if max_results is not None and yielded_count >= max_results:
                break

            if max_pages is not None and page_count >= max_pages:
                break

            # Fetch page
            if next_url:

                if next_url in visited_urls:
                    raise MetaGraphAPIError("Repeated pagination URL detected.")

                visited_urls.add(next_url)

                response = self._fetch_raw_url(next_url)

            else:

                response = self._make_request(
                    endpoint,
                    params=current_params,
                )

                current_params = None

            page_count += 1

            # Validate data
            items = response.get("data", [])

            if not isinstance(items, list):
                raise MetaGraphAPIError(
                    "Invalid pagination response: data must be a list."
                )

            # Yield objects
            for item in items:

                if max_results is not None and yielded_count >= max_results:
                    return

                yield item

                yielded_count += 1

            # find next page
            paging = response.get("paging", {})

            if not isinstance(paging, dict):
                raise MetaGraphAPIError(
                    "Invalid pagination response: paging must be an object."
                )

            next_url = paging.get("next")

            if next_url is None:
                break

            if not isinstance(next_url, str) or not next_url:
                raise MetaGraphAPIError("Invalid pagination URL returned by Meta.")

            self._validate_pagination_url(next_url)

    # Posts
    def get_post_details(
        self,
        post_id: str,
        fields: str = "id,message,created_time,shares",
    ) -> Dict[str, Any]:
        """
        Fetch metadata and requested fields for a single Facebook post.

        post_id:
            Facebook post ID to retrieve.

        fields:
            Comma-separated list of post fields to return from the Graph API.
        """

        post_id = self._validate_object_id(post_id, "post_id")

        return self._make_request(
            post_id,
            params={
                "fields": self._validate_fields(fields),
            },
        )

    def get_all_posts(
        self,
        page_id: Optional[str] = None,
        limit: Optional[int] = None,
        max_results: Optional[int] = None,
        max_pages: Optional[int] = None,
        fields: str = "id,message,created_time,shares",
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieve posts from a Facebook Page using cursor-based pagination.

        page_id:
            Facebook Page ID to query.
            None falls back to PAGE_ID in the environment.

        limit:
            Posts requested per API page.
            None uses Meta's default page size (usually 25).

        max_results:
            Maximum total posts to yield across all pages.
            None yields all available posts.

        max_pages:
            Maximum number of API pages to fetch.
            None fetches all available pages.

        fields:
            Comma-separated list of post fields to request for each post.
        """

        target_page_id = page_id or os.getenv("PAGE_ID")

        if not target_page_id:
            raise ValueError("No Page ID provided or found in environment variables.")

        target_page_id = self._validate_object_id(
            target_page_id,
            "page_id",
        )

        if limit is not None and limit < 1:
            raise ValueError("limit must be greater than zero.")

        params = {
            "fields": self._validate_fields(fields),
        }

        # Preserve Meta's default if no limit was specified.
        if limit is not None:
            params["limit"] = limit

        return self._paginate(
            f"{target_page_id}/posts",
            params=params,
            max_results=max_results,
            max_pages=max_pages,
        )

    def get_all_comments(
        self,
        post_id: str,
        limit: Optional[int] = None,
        max_results: Optional[int] = None,
        max_pages: Optional[int] = None,
        fields: str = "id,message,created_time,from",
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieve comments from a Facebook Post using cursor-based pagination.

        post_id:
            Facebook Post ID to query.

        limit:
            Comments requested per API page.
            None uses Meta's default page size (usually 25).

        max_results:
            Maximum total comments to yield across all pages.
            None yields all available comments.

        max_pages:
            Maximum number of API pages to fetch.
            None fetches all available pages.

        fields:
            Comma-separated list of comment fields to request for each comment.
        """

        if not post_id:
            raise ValueError("No Post ID provided.")

        post_id = self._validate_object_id(
            post_id,
            "post_id",
        )

        if limit is not None and limit < 1:
            raise ValueError("limit must be greater than zero.")

        params = {
            "fields": self._validate_fields(fields),
        }

        # Preserve Meta's default if no limit was specified.
        if limit is not None:
            params["limit"] = limit

        return self._paginate(
            f"{post_id}/comments",
            params=params,
            max_results=max_results,
            max_pages=max_pages,
        )

    def get_all_replies(
        self,
        comment_id: str,
        limit: Optional[int] = None,
        max_results: Optional[int] = None,
        max_pages: Optional[int] = None,
        fields: str = "id,message,created_time,from",
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Retrieve replies from a Facebook Comment using cursor-based pagination.

        comment_id:
            Facebook Comment ID to query.

        limit:
            Replies requested per API page.
            None uses Meta's default page size (usually 25).

        max_results:
            Maximum total replies to yield across all pages.
            None yields all available replies.

        max_pages:
            Maximum number of API pages to fetch.
            None fetches all available pages.

        fields:
            Comma-separated list of reply fields to request for each reply.
        """
        if not comment_id:
            raise ValueError("No Comment ID provided.")

        comment_id = self._validate_object_id(
            comment_id,
            "comment_id",
        )

        if limit is not None and limit < 1:
            raise ValueError("limit must be greater than zero.")

        params = {
            "fields": self._validate_fields(fields),
        }

        # Preserve Meta's default if no limit was specified.
        if limit is not None:
            params["limit"] = limit

        return self._paginate(
            f"{comment_id}/comments",
            params=params,
            max_results=max_results,
            max_pages=max_pages,
        )

    def reply_to_comment(
        self,
        comment_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Post a reply to an existing Facebook comment or reply.

        comment_id:
            Facebook comment ID to reply to.

        message:
            None-empty reply text body

        Returns:
        Meta Graph API response, normally containing the newly created reply ID.
        """

        comment_id = self._validate_object_id(comment_id, "comment_id")
        message = self._validate_message(message)

        return self._make_request(
            f"{comment_id}/comments",
            method="POST",
            data={
                "message": message,
            },
        )

    def delete_comment(
        self,
        comment_id: str,
    ) -> Dict[str, Any]:
        """
        Delete and existing Facebook comment or reply.

        comment_id:
            Facebook comment ID to delete.

        Returns:
            Meta Graph API response, normally {"success": True}
        """

        comment_id = self._validate_object_id(
            comment_id,
            "comment_id",
        )

        return self._make_request(
            comment_id,
            method="DELETE",
        )