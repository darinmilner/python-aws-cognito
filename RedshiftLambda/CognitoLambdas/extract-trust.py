import boto3
import json 
import logging 

logger = logging.getLogger()

sts_client = boto3.client('sts')
session = boto3.Session()
iam_client = session.client("iam")


def lambda_handler(event, context):
    logger.info(f"Event {event}")
    
    role_name = "bucket-role"
    
    update_trust = {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid" : "Lambda-Trust",
          "Effect": "Allow",
          "Principal": { 
            "Service": "lambda.amazonaws.com" 
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }
    
    trust_policy = get_trust_policy(role_name)
    
    if trust_policy:
        logger.info(f"Trust Policy for {role_name} : {trust_policy}")
        print(f"Trust Policy for {role_name} : {trust_policy}")
    else:
        logger.warning("Trust Policy Not Found")
        
    policy = append_trust_policy(role_name, trust_policy, update_trust)
    print(policy)
    
def get_trust_policy(role_name):
    try:
        response = iam_client.get_role(RoleName=role_name)
        trust_policy = response["Role"]["AssumeRolePolicyDocument"]
        logger.info(f"IAM Trust Policy {trust_policy}")
        return trust_policy
    except Exception as e:
        logger.error(f"Error getting trust policy: {e}")
        return {
            "msg" : f"An error occurred {e}",
            "statusCode" : 500
        }
  
  
def update_trust_policy(role_name, new_trust_policy):
    try:
        response = iam_client.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(new_trust_policy)
        )
        print(response)
        return response
    except Exception as e:
        logger.info(f"Error updating trust policy: {e}")
        print(e)
        return None 
    
   
def append_trust_policy(role_name, current_trust_policy, new_statements):
    if "Statement" in current_trust_policy:
        current_trust_policy["Statement"].append(new_statements)
    else:
        current_trust_policy["Statement"] = new_statements
    
    print(current_trust_policy)
    return update_trust_policy(role_name, current_trust_policy)


lambda_handler({}, {})