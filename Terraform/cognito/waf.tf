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

resource "aws_wafv2_web_acl" "cognito_waf" {
  name        = "cognito-ip-restriction-alb"
  description = "WAF for Cognito IP restriction on ALB"
  scope       = "REGIONAL"

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

# SEPARATE WAF Logging Configuration Resource
resource "aws_wafv2_web_acl_logging_configuration" "cognito_waf_logs" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_logs.arn]
  resource_arn            = aws_wafv2_web_acl.cognito_waf.arn

  # Optional: Redact sensitive fields
  redacted_fields {
    single_header {
      name = "authorization"
    }
  }

  redacted_fields {
    single_header {
      name = "cookie"
    }
  }

  # Optional: Redact query string
  redacted_fields {
    query_string {}
  }

  depends_on = [aws_cloudwatch_log_group.waf_logs]
}


# CloudWatch Log Group for WAF
resource "aws_cloudwatch_log_group" "waf_logs" {
  name              = "aws-waf-logs-cognito-waf"
  retention_in_days = var.waf_log_retention_days
  kms_key_id        = aws_kms_key.waf_logs.arn

  tags = {
    Name = "waf-logs-cognito"
  }
}