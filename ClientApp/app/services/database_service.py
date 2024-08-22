import boto3
import botocore
import time 
import uuid
import json 

from app.models.database import Product
from decimal import Decimal
from fastapi import HTTPException
from app.core.config import env_vars


DB_NAME = env_vars.DB_NAME
REGION = env_vars.AWS_REGION

dynamodb = boto3.resource("dynamodb",region_name=env_vars.AWS_REGION)

class DatabaseService:
    def get_all():
        try:
            table = dynamodb.Table(env_vars.DB_NAME)
            items = table.scan()
            return items
        except botocore.exceptions.ClientError:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

    async def create(product_data: dict):
        """
            Function to create a new product in the database using the Product Model
            Example json
            {
                "name" : "Cognito and FastAPI E-Course",
                "price" : 45,
                "description" : "An online course for learning Cognito and FastAPI"
            }
        """
        data = json.loads(json.dumps(product_data), parse_float=Decimal)
        
        try:
            table = dynamodb.Table(env_vars.DB_NAME)
            current_time = get_current_time()
            print(current_time)
            product = Product(name=data["name"], description=data["description"], price=int(data["price"]), id=str(uuid.uuid4()), created_at=current_time, updated_at=current_time)
       
            table.put_item(Item = product.dict())
            return "New Product Created Successfully"
        except botocore.exceptions.ClientError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    def get_product_by_name(name: str):
        try:
            table =dynamodb.Table(env_vars.DB_NAME)
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("name").eq(name)
        )
            if 'Items' in response:
                return response['Items']
            else:
                return None

        except botocore.exceptions.ClientError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
    def delete_product_by_name(name: str):
        try:
            table = dynamodb.Table(env_vars.DB_NAME)
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("name").eq(name)
            )
            if 'Items' in response and response['Items']:
                item_to_delete = response['Items'][0]
                primary_key_value = item_to_delete["id"]
                delete_response = table.delete_item(
                    Key = {
                        "id": primary_key_value
                    }
                )
                return delete_response
            else:
                return {"message": "Item not found"}
        except botocore.exceptions.ClientError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")


# gets currents time 
def get_current_time():
    now = time.time()
    return Decimal(now)