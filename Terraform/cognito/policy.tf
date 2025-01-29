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

// IAM role for unauthenticated users
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

resource "aws_iam_role" "admin" {
  name = "cognito-admin-${local.short-region}"
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

resource "aws_iam_role_policy" "unauthenticated" {
  name   = "unauthenticated-policy-${local.short-region}"
  role   = aws_iam_role.unauthenticated.id
  policy = templatefile("templates/cognito-policy.json", {})
}

resource "aws_iam_role_policy" "admin-role" {
  name   = "admin-policy-${local.short-region}"
  role   = aws_iam_role.admin.id
  policy = templatefile("templates/cognito-admin.json", {})
}
