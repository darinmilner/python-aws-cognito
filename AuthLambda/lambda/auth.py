import requests
import os 

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode


@dataclass_json
@dataclass
class Credentials:
    jwt_token: str
    header: dict[str, str]
    claims: dict[str, str | list[str]]  # list[str] for cognito:groups
    signature: str
    message: str
    

JWK = dict[str, str]


@dataclass
class JWKS:
    keys: list[JWK]
    
jwks = JWKS(
    **requests.get(
        f"https://cognito-idp.{os.environ.get('AWS_REGION')}.amazonaws.com/{os.environ.get('AWS_COGNITO_USER_POOL_ID')}//.well-known/jwks.json"
    ).json()
)
JWK_CACHE:  dict[str, JWK] ={jwk["kid"]: jwk for jwk in jwks.keys}


def get_token_from_bearer(headers) -> Credentials:
    if headers:
        bearer_token = headers["Authorization"]
        return bearer_token
    else:
        raise Exception("Incoorect or missing headers.")
 
 
def verify_jwt(credentials: Credentials) -> bool:
    try: 
        public_key = JWK_CACHE[credentials.header["kid"]]
    except KeyError:
        raise Exception("JWK public key not found")

    key = jwk.construct(public_key)
    decoded_signature = base64url_decode(credentials.signature.encode())

    return key.verify(credentials.message.encode(), decoded_signature)     
  

def get_credentials_from_token(headers) -> Credentials:
    token = get_token_from_bearer(headers)
    token = token.split(" ")[1]
    message, signature = token.rsplit(".", 1)
    try:
        credentials = Credentials(
            jwt_token=token,
            header=jwt.get_unverified_header(token),
            claims=jwt.get_unverified_claims(token),
            signature=signature,
            message=message,
        )
    except JWTError:
        raise Exception("Invalid JWK")
    if not verify_jwt(credentials):
        raise Exception("Invalid JWK")
    return credentials