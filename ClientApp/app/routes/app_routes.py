import json
import requests

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import  HTMLResponse, RedirectResponse 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating  import Jinja2Templates
from pycognito import Cognito 
from pycognito.exceptions import ForceChangePasswordException 
from app.models.auth import Credentials, get_credentials_from_token, get_user_from_session, get_hosted_url 
from app.core.config import env_vars
from app.services.database_service import DatabaseService as db



AWS_DEFAULT_REGION = env_vars.AWS_REGION
AWS_COGNITO_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID
AWS_COGNITO_POOL_NAME = env_vars.AWS_COGNITO_USER_POOL_NAME
AWS_COGNITO_HOSTED_UI_CALLBACK_URL = env_vars.AWS_COGNITO_HOSTED_UI_CALLBACK_URL
AWS_COGNITO_HOSTED_UI_LOGOUT_URL = env_vars.AWS_COGNITO_HOSTED_UI_LOGOUT_URL

templates =  Jinja2Templates(directory="templates")

app_router = APIRouter(prefix="")


@app_router.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
async def health():
    return {"message": "Hello from the Auth Service"}


def prettify_json(data: dict) -> str:
    return json.dumps(data, sort_keys=False, indent=2)


@app_router.get("/products", tags=["App"])
async def products(request: Request):
    if request.session.get("user_credentials"):
        items = db.get_all()
        ctx = {"request": request,  "items" :  items}
        return templates.TemplateResponse("products.html", ctx)
    ctx = {"request": request}
    if (url := get_hosted_url("/oauth2/authorize")) is not None:
        ctx["hosted_url"] = url
    return templates.TemplateResponse("index.html", ctx)

 
@app_router.post("/add-product",status_code=status.HTTP_201_CREATED, tags=["App"]) 
async def create_product(request: Request,  data: dict):
    if request.session.get("user_credentials"):
        msg = await db.create(data)
        return {"message": msg}
   
   
@app_router.get("/product/{name}", tags=["App"])
async def get_product_by_name(request: Request, name: str):
    if request.session.get("user_credentials"):
        item = db.get_product_by_name(name)
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item 
    else:
        raise HTTPException(status_code=401, detail="Unauthorized Access")
 
  
@app_router.delete("/product/{name}", tags=["App"])
async def delete_product_by_name(request: Request, name: str):
    if request.session.get("user_credentials"):
        item = db.delete_product_by_name(name) 
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": f"{name} deleted successfully"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized Access")
    
# TODO: move to auth routes   
@app_router.get("/", tags=["Auth"])
async def index(request: Request):
    if request.session.get("user_credentials"):
        return RedirectResponse(url="/welcome", status_code=status.HTTP_303_SEE_OTHER)
    ctx = {"request": request}
    if (url := get_hosted_url("/oauth2/authorize")) is not None:
        ctx["hosted_url"] = url
    return templates.TemplateResponse("index.html", ctx)
  
  
# TODO: move to auth routes
# Local login endpoint
@app_router.post("/login", tags=["Auth"])
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


# Used by the hosted UI, if enabled
@app_router.get("/callback", tags=["Auth"])
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

# TODO: move to auth routes
@app_router.get("/logout", tags={"Auth"})
async def logout(request: Request):
    request.session.pop("user_credentials", None)
    # If hosted login was used to sign in, redirect to the hosted logout
    # it will ultimately redirect back to `logout_uri`
    if request.session.pop("used_hosted", None):
       url = get_hosted_url("logout", {"logout_uri": AWS_COGNITO_HOSTED_UI_LOGOUT_URL})
       return RedirectResponse(url=url)
    return RedirectResponse(url="/")


@app_router.get("/welcome", tags=["App"])
async def welcome(
    request: Request
):
    ctx = {"request": request}
    if request.session.get("user_credentials"):
        return templates.TemplateResponse("welcome.html", ctx)
    
    if (url := get_hosted_url("/oauth2/authorize")) is not None:
        ctx["hosted_url"] = url
    return templates.TemplateResponse("index.html", ctx)

# TODO: move to user_management
@app_router.get("/user-details", response_class=HTMLResponse,   tags=["App"])
async def user_details(
    request: Request, credentials: Credentials = Depends(get_user_from_session)
):
    claims = credentials.claims
    user_id: str = claims["sub"]
    roles: list[str] = claims.get("cognito:groups", [])
    print(roles)

    return templates.TemplateResponse(
        "userdetails.html",
        {
            "user_id": user_id,
            "request": request,
            "jwt": prettify_json(claims),
            "roles" : roles,
        },
    )
    