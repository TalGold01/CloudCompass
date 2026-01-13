import json
import boto3
import os

# Initialize Bedrock Client
bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1"
)

def lambda_handler(event, context):
    try:
        # Parse Request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        # DEFAULT QUESTION (Test Case)
        question = body.get('question', 'How many hours is the Kubernetes module?')
        kb_id = os.environ.get('KNOWLEDGE_BASE_ID')

        print(f"Asking: {question}")

        # Call Bedrock (The Brain)
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': question},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    # UPDATED: Using your exact Inference Profile ARN from the Playground
                    'modelArn': 'arn:aws:bedrock:us-east-1:349020400385:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0'
                }
            }
        )

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'question': question,
                'answer': response['output']['text'],
                'citations': response.get('citations', [])
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
