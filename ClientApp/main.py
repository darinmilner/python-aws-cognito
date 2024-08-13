from fastapi import FastAPI

from app.routes.auth_routes import auth_router 

app = FastAPI(
    title="FastAPIAWSCognito",
    description="FastAPI simple API with AWS Cognito Auth Service",
    version="1.0.0",
)

@app.get("/")
def index():
    return {"message": "Hello from the Auth Service"}


app.include_router(auth_router)