output "userpool-domain" {
  value = aws_cognito_user_pool_domain.cognito-domain.domain
}

output "app-client-id" {
  value = aws_cognito_user_pool_client.client-app.id
}

output "userpool-id" {
  value = aws_cognito_user_pool.userpool.id
}

output "userpool-name" {
  value = aws_cognito_user_pool.userpool.name
}

output "login-url" {
  value = "https://${aws_cognito_user_pool_domain.cognito-domain.domain}.auth.${var.region}.amazoncognito.com/login?response_type=code&client_id=${aws_cognito_user_pool_client.client-app.id}&redirect_uri=${var.callback-url}"
}

output "logout-urls" {
  value = aws_cognito_user_pool_client.client-app.logout_urls
}

output "hosted-ui-callback" {
  value = aws_cognito_user_pool_client.client-app.callback_urls
}