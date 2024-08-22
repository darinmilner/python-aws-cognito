import botocore
import json

from fastapi import APIRouter, status, Request, Form
from pydantic import EmailStr
from fastapi.responses import  RedirectResponse
from fastapi.templating  import Jinja2Templates

from ..services.auth_service import AuthService
from ..core.dependencies import get_aws_cognito
from app.models.usermodel import UserSignup
from pydantic.error_wrappers import ValidationError 

templates =  Jinja2Templates(directory="templates")
auth_router = APIRouter(prefix="/api/v1/user")


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
        return RedirectResponse("index.html", status_code=status.HTTP_303_SEE_OTHER)
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