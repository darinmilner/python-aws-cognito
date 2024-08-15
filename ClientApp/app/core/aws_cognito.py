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
    
    def logout(self, access_token: str):
        response = self.client.global_sign_out(
            AccessToken = access_token
        )

        return response 


    def confirm_forgot_password(self, data: ConfirmForgotPassword):
        response = self.client.confirm_forgot_password(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
            Password=data.new_password
        )

        return response

    def change_password(self, data: ChangePassword):
        response = self.client.change_password(
            PreviousPassword=data.old_password,
            ProposedPassword=data.new_password,
            AccessToken=data.access_token,
        )

        return response
    
    def check_user_exists(self, email: EmailStr):
        response = self.client.admin_get_user(
            UserPoolId=AWS_COGNITO_USER_POOL_ID,
            Username=email
        )

        return response
    
    
    def resend_confirmation_code(self, email: EmailStr):
        response = self.client.resend_confirmation_code(
            ClientId=AWS_COGNITO_APP_CLIENT_ID,
            Username=email
        )

        return response
