from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/facebook", tags=["Facebook v1"])


@router.get(
    "/",
    summary="Health check",
    description="Checks if the facebook router is currently running.",
    response_description="A JSON object containing the operational status",
)
def health_check() -> dict:
    return {"status": "Facebook Router Operational"}
