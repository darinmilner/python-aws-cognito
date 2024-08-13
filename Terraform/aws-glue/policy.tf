data "aws_iam_policy_document" "glue-assume-role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "glue-role" {
  name               = "Glue IAM role ${local.short-region}"
  assume_role_policy = data.aws_iam_policy_document.glue-assume-role.json
}

data "aws_iam_policy_document" "glue-policy-document" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket",
      "s3:GetBucketAcl",
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = ["*"] #to be specify later
  }
  statement {
    effect = "Allow"
    actions = [
      "glue:*"
    ]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:*:*:*:/aws-glue/*"
    ] #to be specify later
  }
}

resource "aws_iam_policy" "glue-policy" {
  name        = "glue-policy-${local.short-region}-${local.env}"
  description = "Allow glue to get and list object from s3 bucket"
  policy      = data.aws_iam_policy_document.glue-policy-document.json
}

resource "aws_iam_role_policy_attachment" "glue-role-attachment" {
  role       = aws_iam_role.glue-role.name
  policy_arn = aws_iam_policy.glue-policy.arn
}

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