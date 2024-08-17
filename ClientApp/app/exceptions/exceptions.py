from ...main import app 
from fastapi import Request
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request:Request, exc: RequestValidationError):
    return {"details" : exc.errors(), "body": exc.body}