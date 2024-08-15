import requests

from dataclasses import dataclass
from ..core.config import env_vars


JWK = dict[str, str]

@dataclass
class JWKS:
    keys: list[JWK]
    
jwks = JWKS(
    **requests.get(
        f"https://cognito-idp.{env_vars.AWS_REGION}.amazonaws.com/{env_vars.AWS_COGNITO_USER_POOL_ID}//.well-known/jwks.json"
    ).json()
)
JWK_CACHE:  dict[str, JWK] ={jwk["kid"]: jwk for jwk in jwks.keys}
