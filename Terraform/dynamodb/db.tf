resource "aws_dynamodb_table" "db-table" {
  name           = var.table-name
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "name"
    type = "S"
  }

  attribute {
    name = "updatedAt"
    type = "N"
  }

# change secondary index
  global_secondary_index {
    name               = "product-name-index"
    hash_key           = "name"
    range_key          = "updatedAt"
    write_capacity     = 10
    read_capacity      = 10
    projection_type    = "INCLUDE"
    non_key_attributes = ["id"]
  }

  tags = {
    Name        = "${var.table-name}-${local.short-region}"
    Environment = local.env
  }
}

# TODO: ADD DB Autoscaling