# KMS Key for WAF Log Encryption (optional but recommended)
resource "aws_kms_key" "waf_logs" {
  description             = "KMS key for WAF logs encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        # Principal = {
        #   AWS = "arn:aws:iam::${var.account_id}:root"
        # }
        Principal = {
            AWS = "*"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow WAF to use the key"
        Effect = "Allow"
        Principal = {
          Service = "delivery.logs.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "waf-logs-kms-key"
  }
}

resource "aws_kms_alias" "waf_logs" {
  name          = "alias/waf-logs-key"
  target_key_id = aws_kms_key.waf_logs.key_id
}