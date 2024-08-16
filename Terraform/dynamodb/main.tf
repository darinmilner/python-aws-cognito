provider "aws" {
  region = var.region
}

locals {
  short-region = replace(var.region, "-", "")
  env          = "dev"
}
