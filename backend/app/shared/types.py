from typing import Annotated

from pydantic import Field

FBPostId = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description="Meta post id, e.g. 1029384756_5566778899",
    ),
]

FBCommentId = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        description="Meta comment id, e.g. 5566778899_1122334455",
    ),
]

Score = Annotated[
    float,
    Field(ge=0.0, le=1.0, description="Model confidence between 0 and 1"),
]
