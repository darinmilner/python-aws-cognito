import json

from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.responses import  HTMLResponse 
from fastapi.templating  import Jinja2Templates
from app.models.auth import Credentials, get_user_from_session, get_hosted_url 
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
    