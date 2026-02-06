# CardDemo - Terraform Configuration for AWS Deployment
# This configuration deploys the complete serverless architecture

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CardDemo"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Random suffix for unique resource names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

locals {
  project_name = "carddemo"
  name_prefix  = "${local.project_name}-${var.environment}"
  common_tags = {
    Project     = "CardDemo"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
