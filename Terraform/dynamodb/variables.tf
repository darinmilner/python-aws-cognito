variable "region" {
  description = "AWS DynamoDB Region"
  type        = string
  default     = "us-east-1"
}

variable "table-name" {
  description = "DB table name"
  type        = string
  default     = "ProductsTable"
}
