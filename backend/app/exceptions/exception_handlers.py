from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.detail,
            }
        },
        headers=exc.headers,
    )

# Register in main.py:
#   from app.exceptions.exceptions import AppException
#   from app.exceptions.exception_handlers import app_exception_handler
#   app.add_exception_handler(AppException, app_exception_handler)
