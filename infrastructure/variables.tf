variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base name for the project resources"
  type        = string
  default     = "cloud-compass"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
variable "pinecone_api_key" {
  description = "Sensitive API Key for Pinecone"
  type        = string
  sensitive   = true
}

variable "pinecone_host" {
  description = "The Host URL of your Pinecone Index"
  type        = string
}

variable "billing_email" {
  description = "Email to receive budget alerts"
  type        = string
}
