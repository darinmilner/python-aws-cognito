from dataclasses import dataclass

from  urllib  import parse as url_parse 
import requests
from dataclasses_json import dataclass_json
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (  
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from starlette.status import HTTP_403_FORBIDDEN
from .getjwks import JWK_CACHE
from ..core.config import env_vars

AWS_DEFAULT_REGION = env_vars.AWS_REGION
AWS_COGNITO_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_CLIENT_SECRET = env_vars.CLIENT_SECRET
AWS_COGNITO_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID
AWS_COGNITO_POOL_NAME = env_vars.AWS_COGNITO_USER_POOL_NAME
AWS_COGNITO_HOSTED_UI_CALLBACK_URL = env_vars.AWS_COGNITO_HOSTED_UI_CALLBACK_URL
AWS_COGNITO_HOSTED_UI_LOGOUT_URL = env_vars.AWS_COGNITO_HOSTED_UI_LOGOUT_URL

bearer_scheme = HTTPBearer()
#bearer_scheme = OAuth2PasswordBearer(tokenUrl="token")

@dataclass_json
@dataclass
class Credentials:
    jwt_token: str
    header: dict[str, str]
    claims: dict[str, str | list[str]]  # list[str] for cognito:groups
    signature: str
    message: str


def verify_jwt(credentials: Credentials) -> bool:
    try: 
        public_key = JWK_CACHE[credentials.header["kid"]]
    except KeyError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="JWK public key not found"
        )

    key = jwk.construct(public_key)
    decoded_signature = base64url_decode(credentials.signature.encode())

    return key.verify(credentials.message.encode(), decoded_signature)


async def get_token_from_bearer(
    request: Request,
    http_credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Credentials:
    print(http_credentials)
    if http_credentials:
        if not http_credentials.scheme == "bearer":
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Wrong authentication method"
            )

        return http_credentials.credentials


def get_user_from_session(request: Request) -> Credentials:
    if (c := request.session.get("user_credentials")) is None:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": request.url_for("index")},
        )
    else:
        creds = Credentials.from_dict(c)

    if not verify_jwt(creds):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="JWK invalid")

    return creds


async def get_credentials_from_token(
    token: str = Depends(get_token_from_bearer),
) -> Credentials:
    message, signature = token.rsplit(".", 1)
    print(message)
    try:
        credentials = Credentials(
            jwt_token=token,
            header=jwt.get_unverified_header(token),
            claims=jwt.get_unverified_claims(token),
            signature=signature,
            message=message,
        )
    except JWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="JWK invalid")

    if not verify_jwt(credentials):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="JWK invalid")
    return credentials



def get_hosted_url(
    path: str, extra_qs_params: dict = None, override_qs_params: bool = False
) -> str | None:
    if not AWS_COGNITO_HOSTED_UI_CALLBACK_URL or not AWS_COGNITO_HOSTED_UI_LOGOUT_URL:
        return None

    qs_params = {
        "client_id": AWS_COGNITO_CLIENT_ID,
        "response_type": "code",
        "scope": "email+openid",
        "redirect_uri": AWS_COGNITO_HOSTED_UI_CALLBACK_URL,
    }
    if extra_qs_params:
        qs_params = (
            extra_qs_params if override_qs_params else qs_params | extra_qs_params
        )

    url = url_parse.urlunsplit(
        [
            "https",
            f"{AWS_COGNITO_POOL_NAME}.auth.{AWS_DEFAULT_REGION}.amazoncognito.com",
            path,
            url_parse.urlencode(
                qs_params,
                safe="+",  # scope expects `+` delimiters
                quote_via=url_parse.quote,
            ),
            "",
        ]
    )

    return url