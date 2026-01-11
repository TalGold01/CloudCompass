terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "cloud-compass-owner" # <--- UPDATED: Matches your CLI profile name

  # FINOPS: Automatic Tagging
  default_tags {
    tags = {
      Project     = "CloudCompass"
      Environment = "Dev"
      Owner       = "Tal"
      ManagedBy   = "Terraform"
      CostCenter  = "Portfolio-198"
    }
  }
}