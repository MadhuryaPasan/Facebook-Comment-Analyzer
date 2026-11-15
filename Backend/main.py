# Note: try not to define endpoints on main. Always try to use routers
# Rules: always add documentations. (summary, description, response_description,.etc)
from fastapi import FastAPI
from routers.v1 import facebook, analysis, reports

app = FastAPI(title="Facebook Comment Analyzer API", version="1.0")


@app.get(
    "/",
    summary="Health check",
    description="Checks if the main application is currently running.",
    response_description="A JSON object containing the operational status",
)
def health_check() -> dict:
    return {"status": "Main App Operational"}


app.include_router(facebook.router)
app.include_router(analysis.router)
app.include_router(reports.router)
