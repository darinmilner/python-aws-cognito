Python API with AWS Cognito Auth

Create a venv and install the requirements from the requirements.txt file

Create a .env file and fill in the following three fields 
AWS_REGION = "your-region"
AWS_COGNITO_APP_CLIENT_ID = "your-cognito-app-client-id"
AWS_COGNITO_USER_POOL_ID = "your-cognito-userpool-id"

uvicorn main:app to run the app on port 8000

localhost:8000/docs to see the endpoints using the OpenAPI Interface

