# Security Group for ALB
resource "aws_security_group" "alb_sg" {
  name        = "cognito-alb-sg"
  description = "Security group for Cognito ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = local.https_port
    to_port     = local.https_port
    protocol    = "tcp"
    cidr_blocks = var.allowed_ips # Restrict ingress to allowed IPs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Example ALB configuration with Cognito authentication
resource "aws_lb" "cognito_alb" {
  name               = "cognito-alb"
  internal           = true # Set to true if only internal access
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = aws_subnet.private.*.id
}

resource "aws_lb_listener" "cognito_listener" {
  load_balancer_arn = aws_lb.cognito_alb.arn
  port              = local.https_port
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.cognito.arn

  default_action {
    type = "authenticate-cognito"

    authenticate_cognito {
      user_pool_arn       = aws_cognito_user_pool.main.arn
      user_pool_client_id = aws_cognito_user_pool_client.main.id
      user_pool_domain    = aws_cognito_user_pool_domain.main.domain
    }
  }

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}