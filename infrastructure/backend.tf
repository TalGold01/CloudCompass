# 1. Zip the Code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../backend/lambda_function.py"
  output_path = "../backend/lambda_function.zip"
}

# 2. IAM Role
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${random_id.bucket_suffix.hex}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# 3. Permissions (UPDATED with Inference Profile Access)
resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda-bedrock-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "BedrockAccess"
        Action   = [
          "bedrock:RetrieveAndGenerate",
          "bedrock:Retrieve",
          "bedrock:InvokeModel",
          "bedrock:ListFoundationModels",
          "bedrock:GetInferenceProfile",   # <-- Added this
          "bedrock:ListInferenceProfiles"  # <-- Added this
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid      = "MarketplaceAccess"
        Action   = [
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Subscribe",
          "aws-marketplace:Unsubscribe"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Sid      = "LoggingAccess"
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# 4. The Function
resource "aws_lambda_function" "backend" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "${var.project_name}-backend"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 128
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = aws_bedrockagent_knowledge_base.main.id
    }
  }
}

# 5. Public URL (With CORS fix included)
resource "aws_lambda_function_url" "url" {
  function_name      = aws_lambda_function.backend.function_name
  authorization_type = "NONE"
  cors {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
    allow_headers = ["*"]
    max_age      = 86400
  }
}

output "api_endpoint" {
  value = aws_lambda_function_url.url.function_url
}