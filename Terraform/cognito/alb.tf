# # Security Group for ALB
# resource "aws_security_group" "alb_sg" {
#   name        = "cognito-alb-sg"
#   description = "Security group for Cognito ALB"
#   vpc_id      = var.vpc_id

#   ingress {
#     from_port   = local.https_port
#     to_port     = local.https_port
#     protocol    = "tcp"
#     cidr_blocks = var.allowed_ips # Restrict ingress to allowed IPs
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # Example ALB configuration with Cognito authentication
# resource "aws_lb" "cognito_alb" {
#   name               = "cognito-alb"
#   internal           = true # Set to true if only internal access
#   load_balancer_type = "application"
#   security_groups    = [aws_security_group.alb_sg.id]
#   subnets            = var.subnet_ids
# }

# resource "aws_lb_listener" "cognito_listener" {
#   load_balancer_arn = aws_lb.cognito_alb.arn
#   port              = local.https_port
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-2016-08"
#   certificate_arn   = data.aws_acm_certificate.cognito.arn

#   default_action {
#     type = "authenticate-cognito"

#     authenticate_cognito {
#       user_pool_arn       = aws_cognito_user_pool.userpool.arn
#       user_pool_client_id = aws_cognito_user_pool_client.client-app.id
#       user_pool_domain    = aws_cognito_user_pool_domain.cognito-domain.domain
#     }
#   }

#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.cognito_tg.arn
#   }
# }

# # Target Group (example - adjust based on your backend)
# resource "aws_lb_target_group" "cognito_tg" {
#   name     = "cognito-tg"
#   port     = 80
#   protocol = "HTTP"
#   vpc_id   = var.vpc_id

#   health_check {
#     enabled             = true
#     interval            = 30
#     path                = "/health"
#     port                = "traffic-port"
#     protocol            = "HTTP"
#     timeout             = 5
#     healthy_threshold   = 2
#     unhealthy_threshold = 2
#     matcher             = "200"
#   }

#   tags = {
#     Name = "cognito-tg"
#   }
# }