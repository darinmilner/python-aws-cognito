from fastapi import APIRouter, status, Depends, Request, Form
from pydantic import EmailStr
from fastapi.responses import  RedirectResponse
from fastapi.templating  import Jinja2Templates

from ..models.usermodel import ChangePassword, ConfirmForgotPassword, RefreshToken, UserVerify
from ..services.auth_service import AuthService
from ..core.aws_cognito import AWSCognito
from ..core.dependencies import get_aws_cognito

templates =  Jinja2Templates(directory="templates")
management_router = APIRouter(prefix="/api/v1/user")

# GET USER DETAILS
@management_router.get('/userdetails', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def user_details(email: EmailStr, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.user_details(email, cognito)


@management_router.get("/code", tags=["Account Management"])
async def input_code(request: Request):
    ctx = {"request": request}
    if request.session.get("user_credentials"):
        return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)
   
    return templates.TemplateResponse("input-code.html", ctx)


@management_router.post("/code")
async def validate_code(request: Request, code: str = Form(...) , email: EmailStr = Form(...),  cognito: AWSCognito = Depends(get_aws_cognito)):
    errors = []
    ctx = {"request": request}
    try:
        verified_user = UserVerify(email=email, confirmation_code=code)
        AuthService.verify_account(verified_user, cognito)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        errors.append("Please Check your code and try again")
        print(e)
        ctx["errors"] = errors
        return templates.TemplateResponse("input-code.html", ctx)
    

@management_router.post('/verifyaccount', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def verify_account(
    data: UserVerify,
    cognito: AWSCognito = Depends(get_aws_cognito),
):
    return AuthService.verify_account(data, cognito)

# FORGOT PASSWORD
@management_router.post('/forgot-password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def forgot_password(email: EmailStr, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.forgot_password(email, cognito)


# CONFIRM FORGOT PASSWORD
@management_router.post('/confirm-forgot-password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def confirm_forgot_password(data: ConfirmForgotPassword, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.confirm_forgot_password(data, cognito)


# CHANGE PASSWORD
@management_router.post('/change-password', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def change_password(data: ChangePassword, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.change_password(data, cognito)


# GENERATE NEW ACCESS TOKEN
@management_router.post('/new-token', status_code=status.HTTP_200_OK, tags=["Account Management"])
async def new_access_token(refresh_token: RefreshToken, cognito: AWSCognito = Depends(get_aws_cognito)):
    return AuthService.new_access_token(refresh_token.refresh_token, cognito)
