import requests
import json 

from fastapi import FastAPI
from app.core.config import env_vars
from starlette.middleware.sessions import SessionMiddleware
from app.routes.user_management_routes import management_router 
from app.routes.app_routes import app_router


AWS_COGNITO_CLIENT_SECRET = env_vars.CLIENT_SECRET

app = FastAPI(
    title="FastAPIAWSCognito",
    description="FastAPI simple API with AWS Cognito Auth Service",
    version="1.0.0",
)

app.add_middleware(SessionMiddleware, secret_key=env_vars.CLIENT_SECRET)


app.include_router(app_router)
app.include_router(management_router)
