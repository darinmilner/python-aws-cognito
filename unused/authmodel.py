from pydantic_settings import BaseSettings 
from pydantic.types import Any 
from fastapi_cognito import CognitoAuth, CognitoSettings

from ..core.config import env_vars


AWS_REGION = env_vars.AWS_REGION
AWS_COGNITO_APP_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_USER_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID

class AuthSettings(BaseSettings):
    check_expiration: bool = True 
    jwt_header_prefix: str = "Bearer"
    jwt_header_name: str = "Authorization"
    userpools: dict[str, dict[str, Any]] = {
       "us" : {
            "region" : AWS_REGION,
            "userpool_id" : AWS_COGNITO_USER_POOL_ID,
            "app_client_id" : AWS_COGNITO_APP_CLIENT_ID,
        }
    }
    
auth_settings = AuthSettings()

cognito_auth = CognitoAuth(settings=CognitoSettings.from_global_settings(auth_settings), userpool_name="us")