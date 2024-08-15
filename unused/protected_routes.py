from fastapi import Depends, APIRouter, status
from ..models.tokenmodel import cognito_jwt_authorizer_access_token, cognito_jwt_authorizer_id_token


protected_router = APIRouter(prefix='/api/v1/auth')
@protected_router.get("/protected", status_code=status.HTTP_200_OK, tags=["Protected"], dependencies=[Depends(cognito_jwt_authorizer_access_token)])
def logged_in():
    return {
        "message" : "You are logged in"
    }
    
@protected_router.get("/protected-with-id-token", status_code=status.HTTP_200_OK, tags=["Protected"], dependencies=[Depends(cognito_jwt_authorizer_id_token)])
def protected_with_id_token():
    return {"Hello": "World"}