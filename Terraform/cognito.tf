resource "aws_cognito_user_pool" "userpool" {
  name = "app-userpool-${local.short-region}"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length = var.password-length
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "New Account Confirmation"
    email_message        = "Your new account confirmation code is {####}"
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    name                     = "email"
    required                 = true
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    name                     = "fullname"
    required                 = false
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = false
    mutable                  = true
    name                     = "role"
    required                 = false
  }

  tags = {
    Name        = "app-userpool-${local.short-region}"
    Environment = local.env
  }
}

resource "aws_cognito_user_pool_client" "client-app" {
  name = "Python-API-Client"

  user_pool_id                  = aws_cognito_user_pool.userpool.id
  generate_secret               = false
  refresh_token_validity        = 90
  prevent_user_existence_errors = "ENABLED"
  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_ADMIN_USER_PASSWORD_AUTH"
  ]
}

resource "aws_cognito_user_pool_domain" "cognito-domain" {
  domain       = "app-domain-${local.short-region}-${local.env}"
  user_pool_id = aws_cognito_user_pool.userpool.id
}