variable "region" {
  description = "AWS Glue Region"
  type        = string
  default     = "us-east-1"
}

variable "glue_catalog_database_name" {
  description = "Name of the glue catalog database"
  type        = string
}

variable "glue_crawler_name" {
  description = "Name of the glue crawler"
  type        = string
}

variable "s3_bucket_source_name" {
  description = "S3 source bucket for data to be sent to Glue"
  type        = string
}

variable "vpc_id" {
  description = "VPC Id"
  type        = string
}

variable "route_table_id" {
  description = "Route Table ID in the VPC to connect to the Redshift VPC Endpoint"
  type        = string
}

variable "redshift-address" {
  description = "Redshift connection address"
  type        = string
}

variable "redshift-port" {
  description = "Redshift connection port"
  type        = string
}

# TODO: Store in Secret Manager for more security
variable "redshift_admin_password" {
  description = "Redshift admin password"
}

variable "redshift_admin_username" {
  description = "Redshift admin username"
}

variable "glue_jdbc_conn_name" {
  description = "JBDC connection name"
  type        = string
}

variable "redshift-security-group-id" {
  description = "Redshift security group id"
  type        = string
}

variable "redshift-subnet-id" {
  description = "Redshift subnet id"
  type        = string
}

variable "redshift_glue_catalog_database_name" {
  description = "Redshift Glue catalog database name"
}

variable "redshift_glue_crawler_name" {
  description = "Redshift Glue crawler name"
}

