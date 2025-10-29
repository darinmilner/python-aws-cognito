# CloudWatch Dashboard for WAF Metrics
resource "aws_cloudwatch_dashboard" "waf_dashboard" {
  dashboard_name = "WAF-Cognito-Monitoring"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/WAFV2", "AllowedRequests", "WebACL", aws_wafv2_web_acl.cognito_waf.name, "Rule", "allow-from-approved-ips"],
            [".", "BlockedRequests", ".", ".", ".", "."],
            [".", "CountedRequests", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.region
          title   = "WAF Request Counts"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/WAFV2", "AllowedRequests", "WebACL", aws_wafv2_web_acl.cognito_waf.name, "Rule", "allow-from-approved-ips"],
            [".", "BlockedRequests", ".", ".", ".", "."]
          ]
          view    = "pie"
          stacked = false
          region  = var.region
          title   = "WAF Request Distribution"
          period  = 300
        }
      }
    ]
  })
}

# CloudWatch Log Metric Filter for Security Events
resource "aws_cloudwatch_log_metric_filter" "waf_blocked_requests" {
  name           = "WAFBlockedRequests"
  pattern        = "{ ($.action = \"BLOCK\") }"
  log_group_name = aws_cloudwatch_log_group.waf_logs.name

  metric_transformation {
    name      = "WAFBlockedRequests"
    namespace = "WAF/Custom"
    value     = "1"
  }
}

# CloudWatch Alarm for High Block Rate
resource "aws_cloudwatch_metric_alarm" "high_waf_block_rate" {
  alarm_name          = "high-waf-block-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "100"
  alarm_description   = "This alarm triggers when WAF blocked requests exceed threshold"
  alarm_actions       = [] # Add SNS topic ARN for notifications

  dimensions = {
    WebACL = aws_wafv2_web_acl.cognito_waf.name
    Rule   = "all"
  }
}
