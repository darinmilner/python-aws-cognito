import requests
import json 

from fastapi import FastAPI, Depends,  HTTPException, Request, status
from fastapi.responses import  HTMLResponse,  RedirectResponse 
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating  import Jinja2Templates
from pycognito import Cognito 
from pycognito.exceptions import ForceChangePasswordException 
from app.core.config import env_vars
from starlette.middleware.sessions import SessionMiddleware
from app.routes.auth_routes import auth_router 

from app.models.auth import Credentials, get_credentials_from_token, get_user_from_session, get_hosted_url 


AWS_DEFAULT_REGION = env_vars.AWS_REGION
AWS_COGNITO_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_CLIENT_SECRET = env_vars.CLIENT_SECRET
AWS_COGNITO_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID
AWS_COGNITO_POOL_NAME = env_vars.AWS_COGNITO_USER_POOL_NAME
AWS_COGNITO_HOSTED_UI_CALLBACK_URL = env_vars.AWS_COGNITO_HOSTED_UI_CALLBACK_URL
AWS_COGNITO_HOSTED_UI_LOGOUT_URL = env_vars.AWS_COGNITO_HOSTED_UI_LOGOUT_URL


app = FastAPI(
    title="FastAPIAWSCognito",
    description="FastAPI simple API with AWS Cognito Auth Service",
    version="1.0.0",
)

app.add_middleware(SessionMiddleware, secret_key=env_vars.CLIENT_SECRET)

templates =  Jinja2Templates(directory="templates")

@app.get("/products")
async def index(request: Request):
    if request.session.get("user_credentials"):
        return {"message": "You can see the products"}
    else:
        return {"message": "Please Login"}
    
    
@app.get("/")
async def index(request: Request):
    if request.session.get("user_credentials"):
        return RedirectResponse(url="/user", status_code=status.HTTP_303_SEE_OTHER)
    template_ctx = {"request": request}
    # if (url := get_hosted_url("/oauth2/authorize")) is not None:
    #     template_ctx["hosted_url"] = url
    return templates.TemplateResponse("index.html", template_ctx)


# This endpoint requires the access token to be passed in the Authorization header,
# as an alternative to using session cookies.
# `curl http://{host}:{port}/protected -H "Authorization: Bearer {access_token}"`
@app.get("/protected")
async def protected(
    credentials: Credentials = Depends(get_credentials_from_token),
):
    return credentials


@app.get("/health")
def home():
    return {"message": "Hello from the Auth Service"}

def prettify_json(data: dict) -> str:
    return json.dumps(data, sort_keys=False, indent=2)

# Local login endpoint
@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    c = Cognito(AWS_COGNITO_POOL_ID, AWS_COGNITO_CLIENT_ID, username=form_data.username)
    try:
        print(form_data.__dict__)
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
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            "index.html", {"request": request, "errors": ["Something went wrong"]}
        )

    credentials = await get_credentials_from_token(c.access_token)
    request.session["user_credentials"] = credentials.to_dict()
    return RedirectResponse(url="/user", status_code=status.HTTP_303_SEE_OTHER)



# Used by the hosted UI, if enabled
@app.get("/callback")
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
    return RedirectResponse(url="/user")


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user_credentials", None)
    # If hosted login was used to sign in, redirect to the hosted logout
    # it will ultimately redirect back to `logout_uri`
    if request.session.pop("used_hosted", None):
       url = get_hosted_url("logout", {"logout_uri": AWS_COGNITO_HOSTED_UI_LOGOUT_URL})
       return RedirectResponse(url=url)
    return RedirectResponse(url="/")


@app.get("/user", response_class=HTMLResponse)
async def user(
    request: Request, credentials: Credentials = Depends(get_user_from_session)
):
    claims = credentials.claims
    user_id: str = claims["sub"]
    roles: list[str] = claims.get("cognito:groups", [])
    # override roles for demonstrative purposes
    # roles = ["user"]

    return templates.TemplateResponse(
        "user.html",
        {
            "user_id": user_id,
            "request": request,
            "jwt": prettify_json(claims),
            "roles" : roles,
        },
    )



app.include_router(auth_router)
