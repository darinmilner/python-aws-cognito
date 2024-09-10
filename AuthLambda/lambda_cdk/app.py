#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_lambda.auth_lambda_stack import AuthLambdaStack


app = cdk.App()
AuthLambdaStack(app, "AuthLambdaStack")

app.synth()
