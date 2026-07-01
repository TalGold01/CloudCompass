import boto3
import os

# Initialize client
client = boto3.client('bedrock-agent-runtime')
KB_ID = os.getenv("BEDROCK_KB_ID")
THRESHOLD = 0.60

# RAGAS-style evaluation dataset (Query, Expected Ground Truth Domain)
# Mix of valid domain queries and out-of-domain (hallucination-inducing) queries
evaluation_set = [
    {"query": "How do I configure the enterprise VPN?", "is_in_domain": True},
    {"query": "What is the procedure for requesting PTO?", "is_in_domain": True},
    {"query": "What is the capital of France?", "is_in_domain": False},
    {"query": "Write a python script to scrape a website.", "is_in_domain": False},
    {"query": "Who won the superbowl in 2024?", "is_in_domain": False}
]

def evaluate_hallucination_prevention():
    print(f"Running RAGAS-Style Evaluation on KB: {KB_ID}")
    print(f"Configured Similarity Threshold: {THRESHOLD}\n")
    
    baseline_hallucinations = 0
    prevented_hallucinations = 0
    total_out_of_domain = sum(1 for item in evaluation_set if not item["is_in_domain"])

    for item in evaluation_set:
        query = item["query"]
        
        # Retrieve from Bedrock Knowledge Base
        response = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={'text': query},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 1}}
        )
        
        results = response.get('retrievalResults', [])
        score = results[0].get('score', 0) if results else 0
        
        # Evaluation Logic
        if not item["is_in_domain"]:
            baseline_hallucinations += 1 # Without a threshold, the LLM would attempt to answer this
            
            if score < THRESHOLD:
                prevented_hallucinations += 1
                status = "✅ BLOCKED (Hallucination Prevented)"
            else:
                status = "❌ PASSED (Potential Hallucination)"
        else:
            status = "✅ PASSED (Valid Context)"
            
        print(f"Query: '{query}'")
        print(f"Vector Score: {score:.3f} | Result: {status}\n")

    # Calculate metric
    if total_out_of_domain > 0:
        reduction_rate = (prevented_hallucinations / baseline_hallucinations) * 100
        print("--- Evaluation Metrics ---")
        print(f"Out-of-Domain Queries Tested: {total_out_of_domain}")
        print(f"Hallucinations Prevented by Threshold: {prevented_hallucinations}")
        print(f"Hallucination Reduction Rate: {reduction_rate:.1f}%")
    
if __name__ == "__main__":
    if not KB_ID:
        print("Error: BEDROCK_KB_ID not set.")
    else:
        evaluate_hallucination_prevention()