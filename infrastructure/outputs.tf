output "docs_bucket_name" {
  description = "The name of the S3 bucket where you should upload PDFs"
  value       = aws_s3_bucket.knowledge_base_docs.id
}