# Document Entity Extractor (AWS Bedrock PoC)

## Table of Contents

- [Overview](#overview)
    - [AWS Bedrock](#aws-bedrock)
    - [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Locally](#running-locally)

## Overview
This project is a Streamlit web application for extracting structured entities from uploaded documents (PDF, PNG, JPG, etc.) using AWS Bedrock Agents.

![Architecture](docs/architecture-dark.png#gh-dark-mode-only)
![Architecture](docs/architecture.png#gh-light-mode-only)

Users can define custom extraction fields and view the results. This enables automation of manual processes, reducing back-office costs.

![UI](docs/ui-dark.png#gh-dark-mode-only)
![UI](docs/ui.png#gh-light-mode-only)

### AWS Bedrock
This proof of concept was tested on a AWS Bedrock agent using Nova Lite model.

Moreover, this repository is not intended to demonstrate how to implement an agent in AWS Bedrock. However, if you want to reproduce it, the prompt to create one in your account is provided below.

**Agent Prompt:**
```
You are a document extraction agent.

You will receive:
- A document in PDF, PNG, or other file extension.
- A list of extraction objects, each with:
    - `key`: the entity key to extract.
    - `description`: a clear description of what the entity represents.

Your task:
- For each object, extract the corresponding value from the text.
- Return a JSON with each `key` mapped to the extracted value.
- If the value is not found, return `null` for that key.
- Do not include any explanations or extra text, only the JSON output.

Example Input:
{
  "fields": [
    {
      "key": "name",
      "description": "Candidate's name"
    },
    {
      "key": "candidate_resume_summary",
      "description": "Make a summary about the candidate resume"
    },
    {
      "key": "current_job_role",
      "description": "Candidate's current job role"
    }
  ]
}

Expected Output:
{
    "name": "John Doe",
    "candidate_resume_summary": "Experienced Java Developer. Builds scalable enterprise solutions.",
    "current_job_role": "Java Developer"
}

If you cannot find an entity based on the description, return `null` for that key.
```

### Features

- Upload documents for entity extraction
- Results displayed in a user-friendly format
- Uses AWS Bedrock via boto3

## Prerequisites

- AWS credentials and Bedrock agent implementation
- The following `.env` file in `app/.env` (example):

  ```
  AWS_REGION=your-region
  AWS_ACCESS_KEY_ID=your-access-key-id
  AWS_SECRET_ACCESS_KEY=your-secret-access-key
  AWS_BEDROCK_AGENT_ID=your-bedrock-agent-id
  AWS_BEDROCK_AGENT_ALIAS_ID=your-bedrock-agent-alias-id
  ```

## Installation

1. Clone this repository.
2. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r app/requirements.txt
   ```

4. Create your `.env` file in `app/.env` as shown above.

## Running Locally

Start the Streamlit app:

```bash
streamlit run app/main.py
```

Open the provided local URL in your browser to use the application.
