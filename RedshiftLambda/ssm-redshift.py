import boto3 
import time 

client = boto3.client("redshift-data")

response = client.execute_statement(
    ClusterIdentifier="ssm-redshift-cluster",
    Database="dev-db",
    SecretArn="your-redshift-creds-ssm-arn",
    Sql="select * from employees;"
)

query_id = response["Id"]

response = client.describe_statement(Id=query_id)
while True:
    response = client.describe_statement(Id=query_id)
    if (response["Status"] == "FINISJHED"):
        print(f"Query status {response['Status']}")
        break 
    else:
        print(f"Query status {response["Status"]}")
        time.sleep(3)
        print("Three seconds nap time!")
        
response = client.get_statement_result(Id=query_id)
for record in response["Records"]:
    print(record)