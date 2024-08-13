# VPC Gateway Endpoint to connect to Redshift
#create endpoint gateway to allow traffic between s3 and redshift VPC
resource "aws_vpc_endpoint" "s3_redshift" {
  vpc_id            = var.vpc_id
  service_name      = "com.amazonaws.us-east-1.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [var.route_table_id]
}

# Creates a jdbc connection which is also needed to access Redshift from Glue
resource "aws_glue_connection" "glue_jdbc_conn" {
  connection_properties = {
    JDBC_CONNECTION_URL = "jdbc:redshift://${var.redshift-address}:${var.redshift-port}/dev"
    PASSWORD            = var.redshift_admin_password
    USERNAME            = var.redshift_admin_username
  }
  name = var.glue_jdbc_conn_name
  physical_connection_requirements {
    availability_zone = aws_subnet.redshift-serverless-subnet-az1.availability_zone
    security_group_id_list = [
      var.redshift-security-group-id,
    ]
    subnet_id = var.redshift-subnet-id
  }
}
