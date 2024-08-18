from pydantic import BaseModel
from decimal import Decimal


class Product(BaseModel):
    """
        Product Representation
    """  
    id: str  
    name: str
    description : str
    price: int 
    created_at: Decimal
    updated_at: Decimal
