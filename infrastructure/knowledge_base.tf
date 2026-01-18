resource "aws_bedrockagent_knowledge_base" "main" {
  name     = "${var.project_name}-kb"
  role_arn = aws_iam_role.bedrock_role.arn

  knowledge_base_configuration {
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
    }
    type = "VECTOR"
  }

  storage_configuration {
    type = "PINECONE"
    pinecone_configuration {
      connection_string      = var.pinecone_host
      credentials_secret_arn = aws_secretsmanager_secret.pinecone_key.arn
      field_mapping {
        text_field     = "text"
        metadata_field = "metadata"
      }
    }
  }
  
  depends_on = [aws_iam_role_policy.bedrock_policy]
}

resource "aws_bedrockagent_data_source" "s3_docs" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.main.id
  name              = "${var.project_name}-datasource"
  
  data_source_configuration {
    type = "S3"
    s3_configuration {
      bucket_arn = aws_s3_bucket.knowledge_base_docs.arn
    }
  }

  # --- NEW: CHUNKING STRATEGY ---
  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      
      fixed_size_chunking_configuration {
        max_tokens         = 1024  # Bigger chunks for better context
        overlap_percentage = 20    # 20% overlap so sentences aren't cut blindly
      }
    }
  }
  # ------------------------------
}
