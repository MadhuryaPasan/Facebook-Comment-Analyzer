from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/reports", tags=["Reports v1"])


@router.get(
    "/",
    summary="Health check",
    description="Checks if the reports router is currently running.",
    response_description="A JSON object containing the operational status",
)
def health_check() -> dict:
    return {"status": "Reports Router Operational"}
