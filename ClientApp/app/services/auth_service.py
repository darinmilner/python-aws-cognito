from fastapi import HTTPException
from fastapi.responses import JSONResponse
import botocore
from pydantic import EmailStr

from ..core.aws_cognito import AWSCognito
from ..models.usermodel import ChangePassword, ConfirmForgotPassword, UserSignup, UserVerify


class AuthService:  
    def user_signup(user: UserSignup, cognito: AWSCognito):
        response = cognito.user_signup(user)
        return response

    def verify_account(data: UserVerify, cognito: AWSCognito):
        try:
            response = cognito.verify_account(data)
            print(response)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'CodeMismatchException':
                raise HTTPException(
                    status_code=400, detail="The provided code does not match the expected value.")
            elif e.response['Error']['Code'] == 'ExpiredCodeException':
                raise HTTPException(
                    status_code=400, detail="The provided code has expired.")
            elif e.response['Error']['Code'] == 'UserNotFoundException':
                raise HTTPException(
                    status_code=404, detail="User not found")
            elif e.response['Error']['Code'] == 'NotAuthorizedException':
                raise HTTPException(
                    status_code=200, detail="User already verified.")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            return JSONResponse(content={"message": "Account verification successful"}, status_code=200)

    def resend_confirmation_code(email: EmailStr, cognito: AWSCognito):
        try:
            cognito.check_user_exists(email)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                raise HTTPException(
                    status_code=404, detail="User deos not exist")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            try:
                cognito.resend_confirmation_code(email)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'UserNotFoundException':
                    raise HTTPException(
                        status_code=404, detail="User not found")
                elif e.response['Error']['Code'] == 'LimitExceededException':
                    raise HTTPException(
                        status_code=429, details="Limit exceeded")
                else:
                    raise HTTPException(
                        status_code=500, detail="Internal Server")
            else:
                return JSONResponse(content={"message": "Confirmation code sent successfully"}, status_code=200)
            

    def forgot_password(email: EmailStr, cognito: AWSCognito):
        try:
            cognito.forgot_password(email)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                raise HTTPException(
                    status_code=404, detail="User deos not exist")
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise HTTPException(
                    status_code=403, detail="Unverified account")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            return JSONResponse(content={"message": "Password reset code sent to your email address"}, status_code=200)

    def confirm_forgot_password(data: ConfirmForgotPassword, cognito: AWSCognito):
        try:
            cognito.confirm_forgot_password(data)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ExpiredCodeException':
                raise HTTPException(
                    status_code=403, detail="Code expired.")
            elif e.response['Error']['Code'] == 'CodeMismatchException':
                raise HTTPException(
                    status_code=400, detail="Code does not match.")
            else:
                raise HTTPException(status_code=500, detail="Internal Server")
        else:
            return JSONResponse(content={"message": "Password reset successful"}, status_code=200)

    def change_password(data: ChangePassword, cognito: AWSCognito):
        try:
            cognito.change_password(data)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterException':
                raise HTTPException(
                    status_code=400, detail="Access token provided has wrong format")
            elif e.response['Error']['Code'] == 'NotAuthorizedException':
                raise HTTPException(
                    status_code=401, detail="Incorrect username or password")
            elif e.response['Error']['Code'] == 'LimitExceededException':
                raise HTTPException(
                    status_code=429, detail="Attempt limit exceeded, please try again later")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            return JSONResponse(content={"message": "Password changed successfully"}, status_code=200)

    def new_access_token(refresh_token: str, cognito: AWSCognito):
        try:
            response = cognito.new_access_token(refresh_token)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterException':
                raise HTTPException(
                    status_code=400, detail="Refresh token provided has wrong format")
            elif e.response['Error']['Code'] == 'NotAuthorizedException':
                raise HTTPException(
                    status_code=401, detail="Invalid refresh token provided")
            elif e.response['Error']['Code'] == 'LimitExceededException':
                raise HTTPException(
                    status_code=429, detail="Attempt limit exceeded, please try again later")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            content = {
                "message": 'Refresh token generated successfully',
                "accessToken": response['AuthenticationResult']['AccessToken'],
                "expiresIn": response['AuthenticationResult']['ExpiresIn'],
            }
            return JSONResponse(content=content, status_code=200)


    def user_details(email: EmailStr, cognito: AWSCognito):
        try:
            response = cognito.check_user_exists(email)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'UserNotFoundException':
                raise HTTPException(
                    status_code=404, detail="User deos not exist")
            else:
                raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            user = {}
            for attribute in response['UserAttributes']:
                user[attribute['Name']] = attribute['Value']
            return JSONResponse(content=user, status_code=200)