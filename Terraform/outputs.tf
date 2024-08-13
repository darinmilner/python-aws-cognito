output "userpool-domain" {
  value = aws_cognito_user_pool_domain.cognito-domain.domain
}

output "app-client-id" {
  value = aws_cognito_user_pool_client.client-app.id
}

output "userpool-id" {
  value = aws_cognito_user_pool.userpool.id
}