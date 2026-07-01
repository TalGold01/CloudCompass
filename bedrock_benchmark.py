import boto3
import time
import json
import os
import statistics

# Initialize Bedrock clients
bedrock_agent = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')

KB_ID = os.getenv("BEDROCK_KB_ID")
# Updated to match the current Claude 3.5 Haiku production model
MODEL_ID = "anthropic.claude-3-5-haiku-20241022-v1:0" 

def run_benchmark(query: str, iterations: int = 15):
    if not KB_ID:
        print("Error: BEDROCK_KB_ID environment variable not set.")
        return

    latencies = []
    print(f"Starting Benchmark: Decoupled RAG Pipeline ({MODEL_ID})")
    print(f"Targeting Knowledge Base: {KB_ID}\n")
    
    for i in range(iterations):
        start_time = time.time()
        
        # Phase 1: Retrieve
        retrieval_response = bedrock_agent.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={'text': query},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 3}}
        )
        contexts = [res['content']['text'] for res in retrieval_response.get('retrievalResults', [])]
        context_str = " ".join(contexts) if contexts else "No context found."
        
        # Phase 2: Invoke (Generation)
        prompt = f"Context: {context_str}\n\nQuestion: {query}\nAnswer based only on the context."
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        })
        
        bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body
        )
        
        total_time = time.time() - start_time
        latencies.append(total_time)
        print(f"Iteration {i+1:02d} | TTFT & Generation: {total_time:.3f}s")
        
    print("\n--- Final Performance Metrics ---")
    print(f"P50 (Median) Latency: {statistics.median(latencies):.3f}s")
    print(f"P95 (Tail) Latency:   {statistics.quantiles(latencies, n=100)[94]:.3f}s")

if __name__ == "__main__":
    run_benchmark("What are the system requirements?")