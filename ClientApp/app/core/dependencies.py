from .aws_cognito import AWSCognito


def get_aws_cognito() -> AWSCognito:
    return AWSCognito()
