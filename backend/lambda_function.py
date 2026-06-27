
import json
import boto3
import os

# Initialize Bedrock Clients (Decoupled for explicit control)
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name="us-east-1")
bedrock_runtime = boto3.client('bedrock-runtime', region_name="us-east-1")

def lambda_handler(event, context):
    try:
        # Parse Request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        question = body.get('question', 'How many hours is the Kubernetes module?')
        kb_id = os.environ.get('KNOWLEDGE_BASE_ID')
        model_arn = 'arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0'

        print(f"Asking: {question}")

        # ---------------------------------------------------------
        # STEP 1: RETRIEVE (Instead of RetrieveAndGenerate)
        # ---------------------------------------------------------
        retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': question},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5 # Fetch top 5 potential matches
                }
            }
        )
        
        raw_results = retrieve_response.get('retrievalResults', [])
        
        # ---------------------------------------------------------
        # STEP 2: SEMANTIC SIMILARITY THRESHOLDING
        # ---------------------------------------------------------
        # We explicitly filter out low-confidence retrievals to prevent LLM hallucinations.
        SCORE_THRESHOLD = 0.60 
        filtered_contexts = []
        citations = []
        
        for doc in raw_results:
            # Bedrock Pinecone/OpenSearch integrations return a 'score'
            score = doc.get('score', 0)
            
            # Only inject context if it meets the strict confidence threshold
            if score >= SCORE_THRESHOLD or score == 0: 
                filtered_contexts.append(doc['content']['text'])
                if 'location' in doc:
                    citations.append(doc['location'])

        # ---------------------------------------------------------
        # STEP 3: DETERMINISTIC FALLBACK (Zero Hallucination)
        # ---------------------------------------------------------
        if not filtered_contexts:
            print("Threshold not met. Blocking hallucination.")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'question': question,
                    'answer': "I'm sorry, but I do not have enough highly relevant documentation to answer this question confidently.",
                    'citations': []
                })
            }

        # ---------------------------------------------------------
        # STEP 4: CONTEXT INJECTION & GENERATION
        # ---------------------------------------------------------
        context_string = "\n\n---\n\n".join(filtered_contexts)
        
        invoke_response = bedrock_runtime.invoke_model(
            modelId=model_arn,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": "You are a highly precise technical assistant. Answer the user's question ONLY using the provided context. If the context does not explicitly contain the answer, say you don't know. Do not hallucinate.",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Context documentation:\n{context_string}\n\nUser Question:\n{question}"
                    }
                ]
            })
        )
        
        result_body = json.loads(invoke_response['body'].read())
        final_answer = result_body['content'][0]['text']

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'question': question,
                'answer': final_answer,
                'citations': citations
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }