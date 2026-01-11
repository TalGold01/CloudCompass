resource "aws_secretsmanager_secret" "pinecone_key" {
  name        = "${var.project_name}-pinecone-key-${random_id.bucket_suffix.hex}"
  description = "Pinecone API Key for CloudCompass"
}

resource "aws_secretsmanager_secret_version" "pinecone_key_val" {
  secret_id     = aws_secretsmanager_secret.pinecone_key.id
  secret_string = jsonencode({ "apiKey" : var.pinecone_api_key })
}
