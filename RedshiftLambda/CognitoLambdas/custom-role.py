import json 
import logging 

logger = logging.getLogger()

def lambda_handler(event, context):
    """
        Lambda Trigger in cognito can be setup through advanced security features in a cognito userpool
        by adding a type Authentication lambda trigger.  This is a simple lambda for a pre token generation
        trigger to add a custom:role field with the name of the role.
    """
    logger.info(f"Received Event {json.dumps(event)}" )
    
    # Adds a custom claiim to the claimsToAddOrOverride Cognito troken 
    event["response"] = {
        "claimsAndScopeOverrideDetails" : {
            "idTokenGeneration" : {},
            "accessTokenGeneration" : {
                "claimsToAddOrOverride" : {
                    "custom:role": "name-of-role"
                },
                "scopesToAdd" : []
            }
        }
    }