provider "aws" {
  region = var.region
}

locals {
  short-region = replace(var.region, "-", "")
  env          = "dev"
  https_port   = 443
}

resource "aws_cognito_identity_pool_roles_attachment" "policy-attachment" {
  identity_pool_id = aws_cognito_identity_pool.main-pool.id

  roles = {
    "authenticated"   = aws_iam_role.authenticated.arn,
    "unauthenticated" = aws_iam_role.unauthenticated.arn
  }
}

resource "aws_cognito_identity_pool_roles_attachment" "redshift-policy-attachment" {
  identity_pool_id = aws_cognito_identity_pool.main-pool.id

  roles = {
    "authenticated" = aws_iam_role.authenticated.arn
  }

  role_mapping {
    type = "Rules"
    # ambiguous_role_resolution = "AuthenticatedRole"
    ambiguous_role_resolution = "Deny"
    identity_provider         = "${aws_cognito_user_pool.userpool.endpoint}:${aws_cognito_user_pool_client.client-app.id}"

    mapping_rule {
      # The claim name that must be present in the token, for example, "Admin" or "Default".
      claim      = "cognito:groups"
      match_type = "Equals"
      value      = "Admin"
      role_arn   = aws_iam_role.admin.arn
    }

    mapping_rule {
      claim      = "cognito:groups"
      match_type = "Equals"
      value      = "Default"
      role_arn   = aws_iam_role.authenticated.arn
    }
  }
}