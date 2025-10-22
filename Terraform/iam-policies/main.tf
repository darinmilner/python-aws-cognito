# Create and assign an IAM Role Policy to access S3 Buckets
locals {
  short-region = replace(var.aws-region, "-", "")
}

resource "aws_iam_role_policy" "s3-full-access-policy" {
  name = "Redshift-role-s3-policy-test-${local.short-region}"
  role = aws_iam_role.role.id

  policy = <<EOF
{
   "Version": "2012-10-17",
   "Statement": [
     {
       "Effect": "Allow",
       "Action": "s3:*",
       "Resource": "*"
      }
   ]
}
EOF
}

resource "aws_iam_role" "role" {
  name = "test-s3-role-${local.short-region}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": ["ec2.amazonaws.com", "s3.amazonaws.com"]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# Attach the policy to the Redshift role
resource "aws_iam_role_policy_attachment" "attach-s3" {
  count      = 1
  role       = var.create-policy ? data.aws_iam_role.admin-test[count.index].arn : aws_iam_role.role.name
  policy_arn = data.aws_iam_policy.policy.arn
}