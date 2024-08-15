output "userpool-domain" {
  value = aws_cognito_user_pool_domain.cognito-domain.domain
}

output "app-client-id" {
  value = aws_cognito_user_pool_client.client-app.id
}

output "userpool-id" {
  value = aws_cognito_user_pool.userpool.id
}

output "login-url" {
  value = "https://${aws_cognito_user_pool_domain.cognito-domain.domain}.auth.${var.region}.amazoncognito.com/login?response_type=code&client_id=${aws_cognito_user_pool_client.client-app.id}&redirect_uri=${var.callback-url}"
}