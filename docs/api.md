# Comment Analyzer API

The API serves Facebook page comments and their analysis results to any UI. Comments come from the Meta Graph API. The `CommentAnalyzer` class labels each comment with sentiment, intent and aspects, so a company can see what customers think and what they want improved.

## Scope (phase 1)

- **One Facebook page.** `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN` come from `.env`, so no endpoint takes a page id.
- **No authentication yet.**
- **No pagination yet.** List endpoints return all matching results.
- **Base path:** `/api/v1`

| # | Method | Path | Router | Service |
|---|---|---|---|---|
| 1 | GET | `/posts` | `post_comment_router` | `PostCommentService.get_posts` |
| 2 | GET | `/posts/{post_id}` | `post_comment_router` | `PostCommentService.get_post` |
| 3 | GET | `/posts/{post_id}/comments` | `post_comment_router` | `PostCommentService.get_post_comments` |
| 4 | GET | `/comments` | `post_comment_router` | `PostCommentService.get_comments` |
| 5 | GET | `/comments/{comment_id}` | `post_comment_router` | `PostCommentService.get_comment` |
| 6 | POST | `/comments/analyze` | `analysis_router` | `AnalysisService.queue_post_analysis` |

## Enums

| Enum | Values |
|---|---|
| `Sentiment` | `positive`, `neutral`, `negative` |
| `Intent` | `complaint`, `suggestion`, `question`, `praise`, `spam`, `other` |
| `Language` | `en`, `si`, `ta`, `mixed` (Singlish / code-mixed) |
| `TaskStatus` | `queued`, `processing`, `done`, `failed` |

Query parameters are validated by Pydantic models in `app/models/schemas/post.py` and `app/models/schemas/comment.py`. An invalid enum value, an unknown query parameter, or `from` later than `to` returns `422`.

---

## Posts and comments

These endpoints only read data already stored in the database. They never call Facebook directly.

### 1. GET `/api/v1/posts`

Lists the page's posts so the user can choose which one to inspect. Each post includes its comment count and a sentiment breakdown.

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `from` | date (`YYYY-MM-DD`) | no | Posts created on or after this date |
| `to` | date (`YYYY-MM-DD`) | no | Posts created on or before this date |

**Response** `200` → `PostListResponseDTO`

```http
GET /api/v1/posts?from=2026-11-01&to=2026-11-24
```

```json
{
  "items": [
    {
      "post_id": "1029384756_5566778899",
      "message": "Our new rice & curry menu is live! Order now.",
      "created_time": "2026-11-20T10:15:00Z",
      "comment_count": 84,
      "analyzed_count": 80,
      "sentiment_summary": { "positive": 52, "neutral": 18, "negative": 10 }
    }
  ]
}
```

### 2. GET `/api/v1/posts/{post_id}`

Returns one post with its content and overall feedback picture, for a post detail page.

**Response** `200` → `PostResponseDTO` · `404` `POST_NOT_FOUND`

```http
GET /api/v1/posts/1029384756_5566778899
```

```json
{
  "post_id": "1029384756_5566778899",
  "message": "Our new rice & curry menu is live! Order now.",
  "created_time": "2026-11-20T10:15:00Z",
  "comment_count": 84,
  "analyzed_count": 80,
  "sentiment_summary": { "positive": 52, "neutral": 18, "negative": 10 }
}
```

### 3. GET `/api/v1/posts/{post_id}/comments`

Lists all comments on one post, each with its analysis summary. `analysis` is `null` for comments not analyzed yet.

**Query parameters**

| Name | Type | Required | Description |
|---|---|---|---|
| `sentiment` | `Sentiment` | no | Only comments with this sentiment |
| `intent` | `Intent` | no | Only comments with this intent |
| `aspect` | string | no | Only comments that mention this aspect, e.g. `delivery` |
| `analyzed` | bool | no | `true` = analyzed only, `false` = not yet analyzed only |

**Response** `200` → `CommentListResponseDTO` · `404` `POST_NOT_FOUND`

```http
GET /api/v1/posts/1029384756_5566778899/comments?sentiment=negative&intent=complaint
```

```json
{
  "items": [
    {
      "comment_id": "5566778899_1122334455",
      "post_id": "1029384756_5566778899",
      "parent_id": null,
      "message": "Delivery took 2 hours and the food was cold",
      "created_time": "2026-11-20T12:03:00Z",
      "like_count": 5,
      "analysis": {
        "sentiment": "negative",
        "sentiment_score": 0.94,
        "intent": "complaint",
        "aspects": [
          { "aspect": "delivery", "sentiment": "negative", "score": 0.96 },
          { "aspect": "food_quality", "sentiment": "negative", "score": 0.81 }
        ]
      }
    }
  ]
}
```

### 4. GET `/api/v1/comments`

Lists comments across all posts, for page-wide feedback such as all delivery complaints this month. The response has the same shape as endpoint 3.

**Query parameters**

The same as endpoint 3, plus:

| Name | Type | Required | Description |
|---|---|---|---|
| `post_id` | string | no | Only comments on this post |
| `from` | date (`YYYY-MM-DD`) | no | Comments created on or after this date |
| `to` | date (`YYYY-MM-DD`) | no | Comments created on or before this date |

**Response** `200` → `CommentListResponseDTO`

```http
GET /api/v1/comments?aspect=delivery&sentiment=negative&from=2026-11-01&to=2026-11-24
```

```json
{
  "items": [
    {
      "comment_id": "5566778899_1122334455",
      "post_id": "1029384756_5566778899",
      "parent_id": null,
      "message": "Delivery took 2 hours and the food was cold",
      "created_time": "2026-11-20T12:03:00Z",
      "like_count": 5,
      "analysis": {
        "sentiment": "negative",
        "sentiment_score": 0.94,
        "intent": "complaint",
        "aspects": [
          { "aspect": "delivery", "sentiment": "negative", "score": 0.96 }
        ]
      }
    },
    {
      "comment_id": "6677889900_2233445566",
      "post_id": "1029384756_6677889900",
      "parent_id": null,
      "message": "Ordered at 7, still waiting at 8:30",
      "created_time": "2026-11-22T15:10:00Z",
      "like_count": 2,
      "analysis": {
        "sentiment": "negative",
        "sentiment_score": 0.89,
        "intent": "complaint",
        "aspects": [
          { "aspect": "delivery", "sentiment": "negative", "score": 0.92 }
        ]
      }
    }
  ]
}
```

### 5. GET `/api/v1/comments/{comment_id}`

Returns one comment with its full analysis and its replies, so the user can see why it was classified the way it was.

**Response** `200` → `CommentDetailResponseDTO` · `404` `COMMENT_NOT_FOUND`

```http
GET /api/v1/comments/5566778899_1122334455
```

```json
{
  "comment_id": "5566778899_1122334455",
  "post_id": "1029384756_5566778899",
  "parent_id": null,
  "message": "Delivery took 2 hours and the food was cold",
  "created_time": "2026-11-20T12:03:00Z",
  "like_count": 5,
  "analysis": {
    "language": "en",
    "sentiment": "negative",
    "sentiment_score": 0.94,
    "intent": "complaint",
    "aspects": [
      { "aspect": "delivery", "sentiment": "negative", "score": 0.96 },
      { "aspect": "food_quality", "sentiment": "negative", "score": 0.81 }
    ],
    "keywords": ["delivery", "2 hours", "cold"],
    "is_actionable": true,
    "model_version": "analyzer-0.1.0",
    "analyzed_at": "2026-11-20T12:05:10Z"
  },
  "replies": [
    {
      "comment_id": "5566778899_1122334499",
      "message": "Sorry about this! Please DM us your order number.",
      "created_time": "2026-11-20T12:30:00Z"
    }
  ]
}
```

---

## Analysis

### 6. POST `/api/v1/comments/analyze`

Takes a post id and adds that post to the analyzer's task queue. It returns `202 Accepted` immediately with a `task_id`. A background worker then runs `CommentAnalyzer` on every comment of the post and saves the results. Comments that already have results for the current `model_version` are skipped.

**Request body** → `AnalyzeRequest` (unknown fields are rejected)

```json
{ "post_id": "1029384756_5566778899" }
```

**Response** `202` → `AnalyzeTaskResponseDTO` · `404` `POST_NOT_FOUND` · `503` `TASK_QUEUE_UNAVAILABLE` · `422` invalid body

```json
{
  "task_id": "a3f9c2e1-7b4d-4e8a-9c21-5d6e7f8a9b01",
  "post_id": "1029384756_5566778899",
  "status": "queued",
  "queued_at": "2026-11-24T12:40:00Z"
}
```

**Worker flow** (`analyze_post_task`)

1. Load the post's comments that have no analysis for the current `model_version`.
2. Call `CommentAnalyzer.analyze_batch(comments)`, which takes `list[RawComment]` and returns `list[AnalysisResult]`.
3. Save each `AnalysisResult` as a new row in `comment_analyses`. Rows are never overwritten.

Checking a task's progress is not available yet. A `GET /api/v1/tasks/{task_id}` endpoint is planned.

---

## Shared contracts (`app/models/schemas/comment.py`)

The fetcher and the analyzer depend only on these models, never on each other's code.

| Model | Produced by | Consumed by |
|---|---|---|
| `RawComment` | `FacebookCommentFetcher` | `CommentAnalyzer`, DB save |
| `AnalysisResult` | `CommentAnalyzer` | worker task → `comment_analyses` table |

---

## Error format

Every error uses the same shape:

```json
{
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "Post 1029384756_000 does not exist"
  }
}
```

| Status | Code | When |
|---|---|---|
| 404 | `POST_NOT_FOUND` | The `post_id` doesn't exist in the database |
| 404 | `COMMENT_NOT_FOUND` | The `comment_id` doesn't exist in the database |
| 503 | `TASK_QUEUE_UNAVAILABLE` | `POST /comments/analyze` could not add the post to the task queue (e.g. Redis is down) |
| 422 | — | Invalid query parameter or body. FastAPI's default validation response |

---

## Planned (not in phase 1)

- `GET /tasks/{task_id}` to check analysis task status
- Insights endpoints: summary, trends, aspects, suggestions, complaints, keywords
- `POST /sync` to fetch new posts and comments from Facebook through the API
- Pagination on list endpoints
- Authentication and support for multiple pages
