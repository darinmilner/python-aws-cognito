from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    AWS_REGION : str 
    AWS_COGNITO_APP_CLIENT_ID : str 
    AWS_COGNITO_USER_POOL_ID : str 
    AWS_COGNITO_USER_POOL_NAME : str 
    CLIENT_SECRET : str 
    AWS_COGNITO_HOSTED_UI_CALLBACK_URL : str 
    AWS_COGNITO_HOSTED_UI_LOGOUT_URL : str 
    DB_NAME: str 
    
    model_config = SettingsConfigDict(env_file=".env")
    

settings = Settings()

# cache settings to improve performance
@lru_cache
def get_settings():
    return settings 

env_vars = get_settings()
