import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame
from pyspark.sql.functions import to_date, col

args = getResolvedOptions(sys.argv, ['JOB_NAME']) 
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args) 

# Create dynamic frame from glue s3 catalog
inputDF = glueContext.create_dynamic_frame.from_catalog(database="redshift_s3_database", table_name="data_source_bucket", transformation_ctx="inputDF")

# Convert DynamicFrame to DataFrame
inputDF_df = inputDF.toDF()
# Convert contract_date and settlement_date from string to date format
inputDF_df = inputDF_df.withColumn("contract_date", to_date(col("contract_date").cast("string"), "yyyyMMdd"))
inputDF_df = inputDF_df.withColumn("settlement_date", to_date(col("settlement_date").cast("string"), "yyyyMMdd"))
# Apply other transformations and type changes
inputDF_df = inputDF_df.withColumn("id", col("id").cast("int"))
inputDF_df = inputDF_df.withColumn("unit_num", col("unit_num").cast("int"))
inputDF_df = inputDF_df.withColumn("street_num", col("street_num").cast("int"))
inputDF_df = inputDF_df.withColumn("street_name", col("street_name").cast("string"))
inputDF_df = inputDF_df.withColumn("suburb_name", col("suburb_name").cast("string"))
inputDF_df = inputDF_df.withColumn("suburb_postcode", col("suburb_postcode").cast("int"))
inputDF_df = inputDF_df.withColumn("area_size", col("area_size").cast("double"))
inputDF_df = inputDF_df.withColumn("area_unit", col("area_unit").cast("string"))
inputDF_df = inputDF_df.withColumn("sold_price", col("sold_price").cast("int"))
inputDF_df = inputDF_df.withColumn("zoning", col("zoning").cast("string"))
inputDF_df = inputDF_df.withColumn("property_nature", col("property_nature").cast("string"))

# Convert DataFrame back to DynamicFrame
outputDF = DynamicFrame.fromDF(inputDF_df, glueContext, "outputDF")
outputDF.show(5)
# Script generated for node Amazon Redshift
AmazonRedshiftDF = glueContext.write_dynamic_frame.from_options(frame=outputDF, connection_type="redshift", connection_options={"redshiftTmpDir": "s3://aws-glue-assets-youraccount-yourregion/temporary/", "useConnectionProperties": "true", "dbtable": "public.your-redshift-table", "connectionName": "connect_redshift_ETL", "preactions": "CREATE TABLE IF NOT EXISTS public.your-redshift-table (id INTEGER, unit_num INTEGER, street_num INTEGER, street_name VARCHAR, suburb_name VARCHAR, suburb_postcode INTEGER, area_size DOUBLE PRECISION, area_unit VARCHAR, contract_date DATE, settlement_date DATE, sold_price INTEGER, zoning VARCHAR, property_nature VARCHAR); TRUNCATE TABLE public.your-redshift-table;"}, transformation_ctx="AmazonRedshiftDF")

job.commit()