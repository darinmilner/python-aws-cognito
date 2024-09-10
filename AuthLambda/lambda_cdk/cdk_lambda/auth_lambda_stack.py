import os
import subprocess
import aws_cdk 
from aws_cdk import(
    aws_lambda as a_lambda,
    aws_apigateway as apigateway,
    Stack,
    Duration,
)
from dotenv import load_dotenv
from constructs import Construct


load_dotenv()

class AuthLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
      
        
        # Lambda Function for the Django Scim App
        auth_lambda = a_lambda.Function(
            self, 
            id="auth-lambda",
            function_name=f"auth-lambda-{os.getenv('SHORT_REGION')}",
            runtime=a_lambda.Runtime.PYTHON_3_12,
            code=a_lambda.Code.from_asset("./lambda"),
            environment={
                "AWS_REGION" : os.getenv("AWS_REGION"),
            },
            timeout=Duration.minutes(5),
            memory_size=1024,
            handler="index.lambda_handler",
            layers=[self.create_dependencies_layer(self.stack_name, "auth_lambda")]
        )
           
        
        #API Gateway creates an Edge REST API for the Lambda
        api = apigateway.LambdaRestApi(
            self,
            id="auth-gateway",
            handler=auth_lambda,
            proxy=True,
        )
        
        # hello_route = api.root.add_resource("hello")
        # hello_route.add_method("GET")
        
        # admin_route = api.root.add_resource(os.environ.get("DJANGO_ADMIN_URL"))
        # admin_route.add_method("GET")
        
        # Deploy Django static files to S3
        
        aws_cdk.CfnOutput(self, "Apiurl", value=api.url)
        
    def create_dependencies_layer(self, project_name, function_name: str) -> a_lambda.LayerVersion:
        requirements_file = "../requirements.txt"  # requirements.txt
        output_dir = "./build/app"  # temporary directory to store dependencies
        
        subprocess.check_call(f"pip install -r {requirements_file} -t {output_dir}/python".split())
        
        layer_id = f"{project_name}-{function_name}-dependencies"
        layer_code = a_lambda.Code.from_asset(output_dir)
        
        layer = a_lambda.LayerVersion(
                self,
                layer_id,
                code=layer_code,
        )
        
        return layer 
        
