import os
import boto3
import time
import numpy as np
from botocore.exceptions import NoCredentialsError, ClientError

# --- Secure Environment Configuration ---
# Zero hardcoded secrets: Relying on environment variables managed by Terraform/CI
REGION = os.getenv("AWS_REGION", "us-east-1")
KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KB_ID")

# Utilizing a fast, serverless generation model for the RetrieveAndGenerate API
MODEL_ARN = os.getenv(
    "BEDROCK_MODEL_ARN", 
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
)

NUM_REQUESTS = 20
PROMPT = "What are the core IAM security policies deployed in this architecture?"

def run_bedrock_benchmark():
    print(f"🚀 Starting CloudCompass (AWS Bedrock) Latency Benchmark: {NUM_REQUESTS} requests...")
    print("-" * 50)
    
    if not KNOWLEDGE_BASE_ID:
        print("⚠️ Execution Halted: BEDROCK_KB_ID environment variable not set.")
        print("💡 Note: In production, this ID is injected automatically via Terraform outputs or GitHub Actions secrets.")
        return

    try:
        # Boto3 securely inherits credentials from IAM roles (if on EC2/Lambda) or ~/.aws/credentials
        client = boto3.client('bedrock-agent-runtime', region_name=REGION)
    except NoCredentialsError:
        print("⚠️ Execution Halted: No AWS credentials found in the environment.")
        return

    latencies = []

    for i in range(NUM_REQUESTS):
        start_time = time.time()
        try:
            # Hitting the managed RetrieveAndGenerate API
            response = client.retrieve_and_generate(
                input={
                    'text': PROMPT
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                        'modelArn': MODEL_ARN
                    }
                }
            )
            
            latency = (time.time() - start_time) * 1000 # Convert to milliseconds
            latencies.append(latency)
            print(f"Request {i+1:02d}/{NUM_REQUESTS} | Latency: {latency:.2f} ms")
            
            # 1-second breather to avoid AWS API rate limits
            time.sleep(1)
            
        except ClientError as e:
            print(f"Request {i+1:02d} failed (AWS API Error): {e}")
        except Exception as e:
            print(f"Request {i+1:02d} failed: {e}")

    if not latencies:
        return

    # Calculate Enterprise Percentiles
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)
    avg = np.mean(latencies)

    print("\n" + "=" * 50)
    print("📊 CLOUDCOMPASS BENCHMARK RESULTS (AWS Bedrock)")
    print("=" * 50)
    print(f"Total Requests: {len(latencies)}")
    print(f"Average Latency: {avg:.2f} ms")
    print(f"P50 Latency:     {p50:.2f} ms")
    print(f"P95 Latency:     {p95:.2f} ms")
    print(f"P99 Latency:     {p99:.2f} ms")
    print("=" * 50)

if __name__ == "__main__":
    run_bedrock_benchmark()