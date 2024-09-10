import botocore
import json
import requests

from fastapi import APIRouter, status, Request, Form, HTTPException, Depends
from pydantic import EmailStr
from pycognito import Cognito
from fastapi.responses import  RedirectResponse
from fastapi.templating  import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from ..services.auth_service import AuthService
from ..core.dependencies import get_aws_cognito
from app.core.config import env_vars
from app.models.auth import get_hosted_url, get_credentials_from_token
from pycognito.exceptions import ForceChangePasswordException 
from app.models.usermodel import UserSignup
from pydantic.error_wrappers import ValidationError 

AWS_DEFAULT_REGION = env_vars.AWS_REGION
AWS_COGNITO_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID
AWS_COGNITO_POOL_NAME = env_vars.AWS_COGNITO_USER_POOL_NAME
AWS_COGNITO_HOSTED_UI_CALLBACK_URL = env_vars.AWS_COGNITO_HOSTED_UI_CALLBACK_URL
AWS_COGNITO_HOSTED_UI_LOGOUT_URL = env_vars.AWS_COGNITO_HOSTED_UI_LOGOUT_URL

templates =  Jinja2Templates(directory="templates")
auth_router = APIRouter(prefix="")


@auth_router.get("/register",  tags=["Auth"])
def signup(request: Request):
    ctx = {"request": request}
    return templates.TemplateResponse("register.html", ctx)


@auth_router.post("/register", tags=["Auth"])
async def register(request: Request, username: str = Form(...),  password: str = Form(...), email: EmailStr = Form(...)):
    errors = []
    ctx = {"request": request}
    try:
        user = UserSignup(email=email, password=password, fullname=username, role="user")
        AuthService.user_signup(user, get_aws_cognito())
        #TODO: Make account verification page
        return RedirectResponse("input-code.html", status_code=status.HTTP_303_SEE_OTHER)
    except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'UsernameExistsException':
                errors.append("An account with the given email already exists")
                ctx["errors"] = errors
                return templates.TemplateResponse("register.html", ctx)
            else:
                errors.append("Please input a valid email or password")
                ctx["errors"] = errors
                return templates.TemplateResponse("register.html", ctx)
    except ValidationError as e:
        errors.append("Please input a valid email or password")
        errors_list = json.loads(e.json())
        for item in errors_list:
            errors.append(item.get("loc")[0] + ": " + item.get("msg"))
        ctx["errors"]  = errors
        return templates.TemplateResponse("register.html",status_code=status.HTTP_400_BAD_REQUEST, context= ctx)

# TODO: move to user management  
@auth_router.get("/input-code",  tags=["Auth"])   
def input_code(request: Request):
    ctx = {"request": request}
    if request.session.get("user_credentials"):
        return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)
    ctx = {"request": request}
    return templates.TemplateResponse("input-code.html", ctx)


@auth_router.get("/", tags=["Auth"])
async def index(request: Request):
    if request.session.get("user_credentials"):
        return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)
    ctx = {"request": request}
    if (url := get_hosted_url("/oauth2/authorize")) is not None:
        ctx["hosted_url"] = url
    return templates.TemplateResponse("index.html", ctx)

# Used by the hosted UI, if enabled
@auth_router.get("/callback", tags=["Auth"])
async def callback(request: Request):
    code = request.query_params["code"]
    # retrieve tokens from `/oauth2/tokens`
    try:
        url = get_hosted_url(
            "oauth2/token",
            {
                "grant_type": "authorization_code",
                "client_id": AWS_COGNITO_CLIENT_ID,
                "redirect_uri": AWS_COGNITO_HOSTED_UI_CALLBACK_URL,
                "code": code,
            },
            override_qs_params=True,
        )
        r = requests.post(
            url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        tokens = r.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    credentials = await get_credentials_from_token(tokens["access_token"])
    request.session["user_credentials"] = credentials.to_dict()
    request.session["used_hosted"] = True
    return RedirectResponse(url="/welcome")

# Local login endpoint
@auth_router.post("/login", tags=["Auth"])
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    c = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=form_data.username)
    try:
        c.authenticate(password=form_data.password)
        # optionally, use admin_authenticate method for super privileges (bypassing auth challenges)
        # c.admin_authenticate(password=data.password)
    except ForceChangePasswordException:
        # TODO not implemented password change UI
        return templates.TemplateResponse(
            "index.html", {"request": request, "errors": ["Password change required"]}
        )
    except c.client.exceptions.NotAuthorizedException:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "errors": ["Incorrect username or password"]},
        )
    except Exception:
        return templates.TemplateResponse(
            "index.html", {"request": request, "errors": ["Something went wrong"]}
        )

    credentials = await get_credentials_from_token(c.access_token)
    request.session["user_credentials"] = credentials.to_dict()
    return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)

#Logout endpoint
@auth_router.get("/logout", tags={"Auth"})
async def logout(request: Request):
    request.session.pop("user_credentials", None)
    # If hosted login was used to sign in, redirect to the hosted logout
    # it will ultimately redirect back to `logout_uri`
    if request.session.pop("used_hosted", None):
       url = get_hosted_url("logout", {"logout_uri": AWS_COGNITO_HOSTED_UI_LOGOUT_URL})
       return RedirectResponse(url=url)
    return RedirectResponse(url="/")

#Forced password change endpoint
@auth_router.post("/forgot-password", tags = ["Auth"])
async def forgot_password(request: Request, email:EmailStr = Form(...)):
    c = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=email)
    try:
        c.forgot_password(email)
    except botocore.exceptions.ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'UserNotFoundException':
            raise HTTPException(
                status_code=404, detail="User deos not exist")
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise HTTPException(
                status_code=403, detail="Unverified account")
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        return templates.TemplateResponse(
            "forgotpassword.html", {"request": request, "errors": ["Something went wrong"]}
        )
    return RedirectResponse(url="/api/forgot-password/code")

#Get function for password change endpoint
@auth_router.get("/forgot-password", tags = ["Auth"])
async def display_forgot_password(request: Request):
    ctx = {"request": request}
    return templates.TemplateResponse("forgotpassword.html", ctx)


#Get function for password change endpoint
@auth_router.get("/forgot-password/code", tags = ["Auth"])
async def display_forgot_password_code(request: Request):
    ctx = {"request": request}
    return templates.TemplateResponse("forgotpasswordcode.html", ctx)

#Get Code function for password change endpoint
@auth_router.post("/forgot-password/code", tags = ["Auth"])
async def forgot_password_code(request: Request, email:EmailStr = Form(...), code:str = Form(...)):
    c = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=email)
    try:
        c.confirm_forgot_password(code)
    except Exception:
        return templates.TemplateResponse(
            "forgotpassword.html", {"request": request, "errors": ["Something went wrong"]}
        )
