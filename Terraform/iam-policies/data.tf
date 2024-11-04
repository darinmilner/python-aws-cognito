data "aws_iam_role" "admin-test" {
  count = var.create-policy ? 1 : 0
  name = "redshift-glue-assume-role-${local.short-region}"
}

data "aws_iam_policy" "policy" {
  name = "iam-policy-for-ec2"
}