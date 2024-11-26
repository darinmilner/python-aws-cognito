# Pre-Token Cognito Lambda to customize claims in the userpool
import logging 
import json 

logger = logging.getLogger()

def lambda_handler(event, context):
    """
    sample event
        event = {
            "request" : {
                "userAttributes" : {
                    "custom:approved" : "true"
                }
            }
        }
    """
    
    logger.info(f"Received Event {json.dumps(event)}" )
    
    # extract user attributes 
    user_attributes = event["request"]["userAttributes"]
    
    # check if the custom:approve is set to true 
    if user_attributes.get("custom:approved") == "true":
        # allow auth or other logic
        return event
    else:
        raise Exception("User is not approved")