provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Owner       = var.my_name
      Project     = var.environment
      Provisioner = "Terraform"
    }
  }
}

terraform {
  required_version = "~> 1.4.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}