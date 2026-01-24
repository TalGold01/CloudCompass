# Cloud Compass ☁️🧭
> **A Serverless RAG (Retrieval-Augmented Generation) Platform architected on AWS.**

## 📖 Project Overview
Cloud Compass is a secure, cloud-native Knowledge Assistant that allows users to interact with private documentation using Generative AI. Unlike standard chatbots, this system leverages a **Knowledge Base** to ground responses in specific source data, eliminating hallucinations and providing accurate citations.

The infrastructure is fully automated using **Terraform (IaC)**, ensuring a reproducible and version-controlled environment.

## 🏗️ Architecture
The system follows a **Serverless Microservices** architecture to ensure scalability and zero idle costs.

* **Frontend:** React + Vite (Single Page Application).
* **Compute:** AWS Lambda (Python 3.12) via Function URL.
* **AI/LLM:** Amazon Bedrock (Claude 3 Haiku 4.5).
* **Vector Search:** Knowledge Base for Amazon Bedrock (Titan Embeddings v2).
* **Storage:** AWS S3 (Document Storage & Terraform State).
* **Orchestration:** Terraform.

## ⚙️ Technical Implementation & Design Choices

### 1. Infrastructure as Code (Terraform)
Instead of manual console clicking, we defined the entire stack in Terraform.
* **Benefit:** Enables rapid teardown/rebuild and prevents "Configuration Drift."
* **Modules:** Infrastructure is split into `compute`, `storage`, and `security` for modular management.

### 2. RAG Optimization (Chunking Strategy)
We implemented a **Fixed-Size Chunking Strategy** to optimize retrieval accuracy.
* **Max Tokens:** `1024` (Allows for detailed paragraphs vs. short snippets).
* **Overlap:** `20%` (Preserves semantic context across chunk boundaries).
* **Why:** Standard chunking often cuts sentences in half; overlap ensures the model understands the flow of information.

### 3. Security (Least Privilege)
* **IAM Roles:** The Lambda function is granted distinct permissions (`bedrock:InvokeModel`, `bedrock:Retrieve`) rather than an admin wildcard.
* **Environment Variables:** Sensitive IDs (Knowledge Base ID, Model ARNs) are injected via Terraform variables, not hardcoded.

## 🚀 Deployment
**Prerequisites:** AWS CLI, Terraform, Node.js.

1.  **Deploy Infrastructure:**
    ```bash
    cd infrastructure
    terraform init
    terraform apply
    ```
2.  **Run Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 📜 License
MIT