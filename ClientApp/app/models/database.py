from pynamodb.attributes import NumberAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model 
from uuid import UUID 
from pydantic import BaseModel
from core.config import env_vars


class BaseTable(Model):
    class Meta:
        region = env_vars.AWS_REGION
        
        
class ProductNameIndex(GlobalSecondaryIndex["ProductTable"]):
    """
        Global Secondary Index for ProductTable
    """
    class Meta:
        index_name = "product-name-index"
        read_capacity_units = 10 
        write_capacity_units = 10 
        projection = AllProjection()
        
    name = UnicodeAttribute(hash_key=True)
    updated_at = NumberAttribute(range_key=True)
    

class ProductTable(BaseTable):
    """
        Prodcut Table Representation
    """
    
    class Meta(BaseTable.Meta):
        table_name = "ProductsTable"
        
    id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(null=False)
    description = UnicodeAttribute(null=False)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    
    product_name_index = ProductNameIndex()
    
    
class ProductSchema(BaseModel):
    name : str 
    description: str 
    

class ProductSchemaIn(ProductSchema):
    pass 


class ProductSchemaOut(ProductSchema):
    id: UUID 
    updated_at: int 
    created_at: int 
