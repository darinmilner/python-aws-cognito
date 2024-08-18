import boto3
import botocore
import time 
import uuid
import json 

from models.database import Product
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
        

    async def create(data: dict):
        try:
            table = dynamodb.Table(env_vars.DB_NAME)
            now = time.time()
            product = Product()
            item = {
                "id": str(uuid.uuid4()),
                "name": data["name"],
                "price": data["price"],
                "createdAt" : now,
                "updatedAt" : now  
            }
            item = json.loads(json.dumps(item), parse_float=Decimal)
            table.put_item(Item = item)
            return "New Product Created Successfully"
        except botocore.exceptions.ClientError:
            raise HTTPException(status_code=500, detail="Internal Server Error")