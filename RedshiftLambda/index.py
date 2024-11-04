from botocore.exceptions import ClientError
import botocore.session as s
import boto3.session
import json
import boto3

from botocore.exceptions import WaiterError
from botocore.waiter import WaiterModel
from botocore.waiter import create_waiter_with_client

region = "us-east-1"
bc_session = s.get_session()
session = boto3.Session(
        botocore_session=bc_session,
        region_name=region,
    )

# Setup the client
client = session.client("redshift-data")
# Create custom waiter for the Redshift Data API to wait for finish execution of current SQL statement
waiter_name = 'DataAPIExecution'
delay=2
max_attempts=3

#Configure the waiter settings
waiter_config = {
  'version': 2,
  'waiters': {
    'DataAPIExecution': {
      'operation': 'DescribeStatement',
      'delay': delay,
      'maxAttempts': max_attempts,
      'acceptors': [
        {
          "matcher": "path",
          "expected": "FINISHED",
          "argument": "Status",
          "state": "success"
        },
        {
          "matcher": "pathAny",
          "expected": ["PICKED","STARTED","SUBMITTED"],
          "argument": "Status",
          "state": "retry"
        },
        {
          "matcher": "pathAny",
          "expected": ["FAILED","ABORTED"],
          "argument": "Status",
          "state": "failure"
        }
      ],
    },
  },
}

waiter_model = WaiterModel(waiter_config)
custom_waiter = create_waiter_with_client(waiter_name, waiter_model, client)

query_str = "create schema taxischema;"
db="redshift-db-name"
cluster_id = "cluster-id"
res = client.execute_statement(Database= db, Sql= query_str, ClusterIdentifier= cluster_id, DbUser="user")
id=res["Id"] #returns the executed SQL Id
# waits for the statement to finish
try:
    custom_waiter.wait(Id=id)
    print("Done waiting to finish Data API.")
except WaiterError as e:
    print (e)
    
# create a table
query_str = 'create table taxischema.nyc_greentaxi(\
vendorid varchar(10),\
lpep_pickup_datetime timestamp,\
lpep_dropoff_datetime timestamp,\
store_and_fwd_flag char(1),\
ratecodeid int,\
pulocationid int,\
dolocationid int,\
passenger_count int,\
trip_distance decimal(8,2),\
fare_amount decimal(8,2),\
extra decimal(8,2),\
mta_tax decimal(8,2),\
tip_amount decimal(8,2),\
tolls_amount decimal(8,2),\
ehail_fee varchar(100),\
improvement_surcharge decimal(8,2),\
total_amount decimal(8,2),\
payment_type varchar(10),\
trip_type varchar(10),\
congestion_surcharge decimal(8,2)\
)\
sortkey (vendorid);'

res = client.execute_statement(Database= db, Sql= query_str, ClusterIdentifier= cluster_id, DbUser="user")
id=res["Id"]

json_resp = json.dumps(res)