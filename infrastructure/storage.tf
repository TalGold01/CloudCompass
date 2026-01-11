# 1. Random ID to ensure bucket name is globally unique
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 2. The Bucket for your PDFs (Knowledge Base Data)
resource "aws_s3_bucket" "knowledge_base_docs" {
  bucket = "${var.project_name}-docs-${random_id.bucket_suffix.hex}"

  # SAFETY: Allows Terraform to delete the bucket even if it has files in it 
  # (Useful for portfolio projects so you don't get stuck with errors later)
  force_destroy = true
}

# 3. Security: Block ALL public access (No accidental leaks)
resource "aws_s3_bucket_public_access_block" "docs_block" {
  bucket = aws_s3_bucket.knowledge_base_docs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 4. Security: Encrypt data at rest (AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "docs_encrypt" {
  bucket = aws_s3_bucket.knowledge_base_docs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 5. FinOps/Safety: Enable Versioning (Keeps history if you overwrite a file)
resource "aws_s3_bucket_versioning" "docs_versioning" {
  bucket = aws_s3_bucket.knowledge_base_docs.id
  versioning_configuration {
    status = "Enabled"
  }
}