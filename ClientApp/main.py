from fastapi import FastAPI, Depends 
from app.routes.auth_routes import auth_router 

from app.models.getjwks import jwks
from app.models.cognitojwt import JWTBearer

app = FastAPI(
    title="FastAPIAWSCognito",
    description="FastAPI simple API with AWS Cognito Auth Service",
    version="1.0.0",
)


auth = JWTBearer(jwks)


@app.get("/")
def index():
    return {"message": "Hello from the Auth Service"}

@app.get("/secure", dependencies=[Depends(auth)])
async def secure() -> dict:
    return {"message": "I am secured by Cognito"}


app.include_router(auth_router)
