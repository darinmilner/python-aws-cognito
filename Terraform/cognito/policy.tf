# IAM role to use with authenticated identities
resource "aws_iam_role" "authenticated" {
  name = "cognito-authenticated-${local.short-region}"
  assume_role_policy = templatefile(
    "templates/cognito-assume-role-policy.json",
    {
      pool_id                          = "${aws_cognito_identity_pool.main-pool.id}",
      authenticated_or_unauthenticated = "authenticated"
    }
  )
}

// Policy to use with authenticated identities
resource "aws_iam_role_policy" "authenticated" {
  name   = "authenticated-policy-${local.short-region}"
  role   = aws_iam_role.authenticated.id
  policy = templatefile("templates/cognito-policy.json", {})
}

resource "aws_cognito_identity_pool_roles_attachment" "policy-attachment" {
  identity_pool_id = aws_cognito_identity_pool.main-pool.id
  roles = {
    "authenticated"   = aws_iam_role.authenticated.arn,
    "unauthenticated" = aws_iam_role.unauthenticated.arn
  }
}

resource "aws_iam_role" "unauthenticated" {
  name = "cognito-unauthenticated-${local.short-region}"
  assume_role_policy = templatefile(
    "templates/cognito-assume-role-policy.json",
    {
      pool_id                          = "${aws_cognito_identity_pool.main-pool.id}",
      authenticated_or_unauthenticated = "unauthenticated"
    }
  )
}

resource "aws_iam_role_policy" "unauthenticated" {
  name   = "unauthenticated-policy-${local.short-region}"
  role   = aws_iam_role.unauthenticated.id
  policy = templatefile("templates/cognito-policy.json", {})
}
