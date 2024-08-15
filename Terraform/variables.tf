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

variable "callback-url" {
  description = "Default Callback URL"
  type = string
  default = "http://localhost:8000/auth/callback"
}