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
  type        = string
  default     = "http://localhost:8000/callback"
}

variable "userpool-name" {
  description = "Cognito User Pool Name"
  type        = string
  default     = "magnolia-app-userpool"
}

variable "allowed_ips" {
  description = "List of allowed IP addresses/CIDR blocks"
  type        = list(string)
  default     = ["192.168.1.0/24", "10.0.0.0/16"] # Replace with your network IPs
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "List of Subnet IDs"
  type        = list(string)
}

variable "certificate_arn" {
  description = "ARN of Certificate for Cognito domain"
  type = string
}