import boto3 
from pydantic import EmailStr 

from ..models.usermodel import ChangePassword, ConfirmForgotPassword, UserSignIn, UserSignup, UserVerify
from .config import env_vars


AWS_REGION = env_vars.AWS_REGION
AWS_COGNITO_APP_CLIENT_ID = env_vars.AWS_COGNITO_APP_CLIENT_ID
AWS_COGNITO_USER_POOL_ID = env_vars.AWS_COGNITO_USER_POOL_ID


class AWSCognito:
    def __init__(self):
        self.client = boto3.client("cognito-idp", region_name=AWS_REGION)
        
    def user_signup(self, user: UserSignup):
        
        response = self.client.sign_up(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            Username=user.email,
            Password=user.password,
            UserAttributes=[
                {
                    "Name": "custom:fullname",
                    "Value": user.fullname,
                },
                {
                    "Name": "custom:role",
                    "Value": user.role,
                },
            ],
        )
        
        return response 
    
    def user_signin(self, data: UserSignIn):
        response = self.client.initiate_auth(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME" : data.email,
                "PASSWORD" : data.password
            }
        )
        
        return response 
    
    def new_access_token(self, refresh_token: str):
        response = self.client.initiate_auth(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            }
        )

        return response
    
    def verify_account(self, data: UserVerify):
        response = self.client.confirm_sign_up(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
        )

        return response