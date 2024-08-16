Python API with AWS Cognito Auth

Create a venv and install the requirements from the requirements.txt file

Create a .env file and fill in the following fields 
AWS_REGION = "your-region"
AWS_COGNITO_APP_CLIENT_ID = "your-cognito-app-client-id"
AWS_COGNITO_USER_POOL_ID = "your-cognito-userpool-id"
CLIENT_SECRET = "a secure secret string to be used by the auth middleware"
AWS_COGNITO_USER_POOL_NAME = "your-userpool-name"
AWS_COGNITO_HOSTED_UI_CALLBACK_URL  = "callback for using the hosted UI"
AWS_COGNITO_HOSTED_UI_LOGOUT_URL = "Hosted UI Logout URL"
DB_NAME = "dynamodb-table-name"

uvicorn main:app to run the app on port 8000

localhost:8000/docs to see the endpoints using the OpenAPI Interface

In order to create a user this app uses AWS Cognito to create users in a userpool and authenticate them to the protected endpoints
A userpool is created in Cognito using AWS Cognito as the identity provider.  It can also be configured to use a third party identity provider such as Google or SAML. 
A user will signup and provide a username, email, and password
The new user must confirm their email with a code that will be sent by AWS Cognito
The user can then access the login page (Homepage)
The needed permissions are also created to allow the authenticated user access to DynamoDB so they can view the data inside the database

Terraform IAC is used to create the Cognito Resources (Terraform/cognito folder) as well as the DynamoDB database (Terraform/dynamodb folder)