locals {
  environment = replace(var.environment, "_", "-")
}

variable "aws_region" {
  description = "AWS Region to deploy resources"
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name we are building"
  default     = "kinesis_twitter"
}

variable "my_name" {
  description = "Meu nome"
  default     = "Camila"
}

variable "tags" {
  description = "Default tags for this environment"
  default     = {}
}

