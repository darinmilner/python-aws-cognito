resource "aws_wafv2_ip_set" "allowed_ips" {
  name               = "cognito-allowed-ips"
  description        = "IP addresses allowed to access Cognito via ALB"
  scope              = "REGIONAL" # Required for ALB
  ip_address_version = "IPV4"
  addresses          = var.allowed_ips

  tags = {
    Name = "cognito-allowed-ips"
  }
}

# WAF Web ACL (REGIONAL scope for ALB)
resource "aws_wafv2_web_acl" "cognito_waf" {
  name        = "cognito-ip-restriction-alb"
  description = "WAF for Cognito IP restriction on ALB"
  scope       = "REGIONAL" # Required for ALB

  default_action {
    block {}
  }

  rule {
    name     = "allow-from-approved-ips"
    priority = 1

    action {
      allow {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.allowed_ips.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "allow-from-approved-ips"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "cognito-ip-restriction-alb"
    sampled_requests_enabled   = true
  }

  tags = {
    Name = "cognito-ip-restriction-alb"
  }
}
