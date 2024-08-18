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
            # TODO: create a function that returns the current time and create a UI HTML page to create a product and get a product by 
            # TODO: name and by id
            now = time.time()
            current_time = Decimal(now)
            product = Product(name=data["name"], description=data["description"], price=int(data["price"]), id=str(uuid.uuid4()), created_at=current_time, updated_at=current_time)
       
            table.put_item(Item = product.dict())
            return "New Product Created Successfully"
        except botocore.exceptions.ClientError:
            raise HTTPException(status_code=500, detail="Internal Server Error")