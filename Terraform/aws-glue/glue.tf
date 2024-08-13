#create glue catalog database
resource "aws_glue_catalog_database" "glue-catalog-database" {
  name = "${var.glue_catalog_database_name}-${local.short-region}"
}

#create glue crawler
resource "aws_glue_crawler" "glue-crawler" {
  database_name = var.glue_catalog_database_name
  name          = "${var.glue_crawler_name}-${local.short-region}"
  role          = aws_iam_role.glue-role.arn
  s3_target {
    path = format("s3://%s", var.s3_bucket_source_name)
  }
}

# Based on the Redshift catalog table, we can add steps in a Glue job to transform the data.
# Common transformations include filtering, converting formats, appending columns, and more
#create redshift catalog database
resource "aws_glue_catalog_database" "redshift-catalog-database" {
  name = "${var.redshift_glue_catalog_database_name}-${local.short-region}"
}

#create redshift to glue crawler
resource "aws_glue_crawler" "redshift-crawler" {
  database_name = "${var.redshift_glue_catalog_database_name}-${local.short-region}"
  name          = var.redshift_glue_crawler_name
  role          = aws_iam_role.glue-role.arn 
  jdbc_target {
    connection_name = aws_glue_connection.glue_jdbc_conn.name
    path            = "dev/public/redshift-table" #db schema and table name
  }
}
