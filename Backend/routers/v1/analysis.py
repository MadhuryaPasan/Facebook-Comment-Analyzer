from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis v1"])


@router.get(
    "/",
    summary="Health check",
    description="Checks if the analysis router is currently running.",
    response_description="A JSON object containing the operational status",
)
def health_check() -> dict:
    return {"status": "Analysis Router Operational"}
