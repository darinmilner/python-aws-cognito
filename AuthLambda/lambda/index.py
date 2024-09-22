import logging
import json
from auth import get_credentials_from_token

logger = logging.getLogger()

def lambda_handler(event, context):
    """
        Example auth event with bearer token
        event = {
            "headers" : {
            "Authorization" : "Bearer 1234567.fgdfgd.io90"
        }
    }
    """ 
    logger.info(event)
  
    headers = event["headers"]    
    try:
        get_credentials_from_token(headers=headers)
        return json.dumps({
            "statusCode" : 200,
            "message" : "Token is valid"
        })
    except Exception as e:
        logger.error(e)
        return json.dumps({
            "statusCode" : 500,
            "message" : "Something went wrong"
        })       
