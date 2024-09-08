from fastapi import FastAPI
from app.core.config import env_vars
from starlette.middleware.sessions import SessionMiddleware
from app.routes.user_management_routes import management_router 
from app.routes.app_routes import app_router
from app.routes.auth_routes import auth_router
from app.core.log_config import init_loggers


# AWS_COGNITO_CLIENT_SECRET = env_vars.CLIENT_SECRET
log = init_loggers()

app = FastAPI(
    title="FastAPIAWSCognito",
    description="FastAPI simple API with AWS Cognito Auth Service",
    version="1.0.0",
)


app.add_middleware(SessionMiddleware, secret_key=env_vars.CLIENT_SECRET)

app.include_router(app_router)
app.include_router(auth_router)
app.include_router(management_router)


# health check
@app.get("/health")
def health():
    log.info("app is running")
    log.debug("Up and Running")
    return {"result": "healthy"}
