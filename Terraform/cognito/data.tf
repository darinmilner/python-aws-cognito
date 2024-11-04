data "aws_iam_role" "default-test" {
  name = "ec2-s3-role-${local.short-region}"
}

data "aws_iam_role" "admin-test" {
  name = "redshift-glue-assume-role-${local.short-region}"
}
