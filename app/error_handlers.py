# from fastapi import Request, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from app.logger import logger  # import the logger we just created

# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     logger.warning(f"Validation error: {exc.errors()} on {request.url}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Validation failed",
#             "details": exc.errors()
#         }
#     )

# async def http_exception_handler(request: Request, exc: HTTPException):
#     logger.error(f"HTTPException: {exc.detail} on {request.url}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"error": exc.detail}
#     )

# async def unhandled_exception_handler(request: Request, exc: Exception):
#     logger.exception(f"Unhandled error on {request.url}")
#     return JSONResponse(
#         status_code=500,
#         content={"error": "Internal server error"}
#     )

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.logger import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handles FastAPI/Pydantic validation errors (422).
    """
    logger.warning(
        f"Validation error on {request.method} {request.url}: {exc.errors()}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles custom or raised HTTP exceptions from FastAPI.
    """
    logger.error(
        f"HTTP {exc.status_code} on {request.method} {request.url}: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected server errors (500).
    Logs full traceback.
    """
    logger.exception(
        f"Unhandled exception on {request.method} {request.url}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )
