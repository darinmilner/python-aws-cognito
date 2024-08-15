import requests

from ..core.config import env_vars
from .cognitojwt import JWKS

jwks = JWKS.parse_obj(
    requests.get(
        f"https://cognito-idp.{env_vars.AWS_REGION}.amazonaws.com/{env_vars.AWS_COGNITO_USER_POOL_ID}//.well-known/jwks.json"
    ).json()
)
