import boto3
import json
import logging

logger = logging.getLogger()


def lambda_handler(event, context):
    # Assume SecondaryRole to get temporary credentials
    sts_client = boto3.client("sts")
    response = sts_client.assume_role(
        RoleArn="arn:aws:iam::<AccountID>:role/SecondaryRole",
        RoleSessionName="AssumeSecondaryRoleSession",
    )

    # Extract temporary credentials
    creds = response["Credentials"]
    iam_client = boto3.client(
        "iam",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )

    try:
        # Now you can call IAM actions using the temporary credentials:
        # Retrieves information about the specified role, including the role’s path, GUID, ARN,
        # and the role’s trust policy that grants permission to assume the role. For more information about roles
        role_name = "SomeRoleToInspect"
        role_info = iam_client.get_role(RoleName=role_name)
        logger.info("Role info:", role_info)
    except Exception as e:
        logger.error("An error occurred.")
        return json.dumps({"msg": f"Error {e}", "status": 500})

    # If needed, update assume role policy:
    new_policy_document = """{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": { "Service": "ec2.amazonaws.com" },
          "Action": "sts:AssumeRole"
        },
      ]
    }"""

    try:
        # Updates The Trust Policy
        iam_client.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=new_policy_document
        )
    except Exception as e:
        logger.error("An error occurred.")
        return json.dumps({"msg": f"Error {e}", "status": 500})

    policy_document = """{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": [
              "cognito-identity:*",
              "iam:getrole*"
            ],
            "Resource": [
              "*"
            ]
          }
        ]
      }"""

    try:
        # Creates a new policy
        iam_client.create_policy(
            PolicyName="your-policy-name", PolicyDocument=policy_document
        )
    except Exception as e:
        logger.error("An error occurred.")
        return json.dumps({"msg": f"Error {e}", "status": 500})

    return json.dumps({"msg": "Success", "status": 200})
