from fastapi import APIRouter, status, Depends
from pydantic import EmailStr


from ..models.usermodel import AccessToken, ChangePassword, ConfirmForgotPassword, RefreshToken, UserSignIn, UserSignup, UserVerify
from ..services.auth_service import AuthService
from ..core.aws_cognito import AWSCognito
from ..core.dependencies import get_aws_cognito


management_router = APIRouter(prefix="/api/v1/auth")


# USER SIGNUP
@management_router.post('/signup', status_code=status.HTTP_201_CREATED, tags=["Account Management"])
async def signup_user(user: UserSignup, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.user_signup(user, cognito)

# GET USER DETAILS
@management_router.get('/userdetails', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def user_details(email: EmailStr, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.user_details(email, cognito)


@management_router.post('/verifyaccount', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def verify_account(
    data: UserVerify,
    cognito: AWSCognito = Depends(get_aws_cognito),
):
    return AuthService.verify_account(data, cognito)

# FORGOT PASSWORD
@management_router.post('/forgot_password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def forgot_password(email: EmailStr, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.forgot_password(email, cognito)


# CONFIRM FORGOT PASSWORD
@management_router.post('/confirm_forgot_password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def confirm_forgot_password(data: ConfirmForgotPassword, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.confirm_forgot_password(data, cognito)


# CHANGE PASSWORD
@management_router.post('/change_password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def change_password(data: ChangePassword, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.change_password(data, cognito)


# GENERATE NEW ACCESS TOKEN
@management_router.post('/new_token', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def new_access_token(refresh_token: RefreshToken, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.new_access_token(refresh_token.refresh_token, cognito)
