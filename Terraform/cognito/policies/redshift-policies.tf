# Redshift Connection Policies
# Create an IAM Role for Redshift
resource "aws_iam_role" "redshift-role" {
  name = "redshift-glue-assume-role-${local.short-region}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "redshift.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = {
    Name        = "Redshift assume role for glue"
    ShortRegion = local.short-region
    Env         = local.env
  }
}
# Create and assign an IAM Role Policy to access S3 Buckets
resource "aws_iam_role_policy" "redshift-s3-full-access-policy" {
  name = "Redshift-role-s3-policy-${local.short-region}"
  role = aws_iam_role.redshift-role.id

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

# Get the AmazonRedshiftAllCommandsFullAccess policy
data "aws_iam_policy" "redshift-full-access-policy" {
  name = "AmazonRedshiftAllCommandsFullAccess"
}

# Attach the policy to the Redshift role
resource "aws_iam_role_policy_attachment" "attach-s3" {
  role       = aws_iam_role.redshift-role.name
  policy_arn = data.aws_iam_policy.redshift-full-access-policy.arn
}