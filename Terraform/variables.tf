variable "region" {
  description = "AWS Cognito Region"
  type        = string
  default     = "us-east-1"
}

variable "password-length" {
  description = "Minimum Password Length"
  type        = number
  default     = 6
}