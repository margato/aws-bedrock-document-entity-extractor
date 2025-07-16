import json
import os

import boto3
from cachetools import LRUCache

from document_parser import convert_to_pdf_if_needed, get_ocr_from_pdf_bytes, sha256

AWS_REGION = os.getenv("AWS_REGION")
AGENT_ID = os.getenv("AWS_BEDROCK_AGENT_ID")
AGENT_ALIAS_ID = os.getenv("AWS_BEDROCK_AGENT_ALIAS_ID")

session = boto3.Session(
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

bedrock_agent_runtime = session.client("bedrock-agent-runtime")
textract = session.client("textract")

llm_cache = LRUCache(maxsize=5)

def call_agent(context: str, document_bytes: bytes, media_type: str, extraction_fields: list):
    pdf_bytes = convert_to_pdf_if_needed(document_bytes, media_type)
    ocr_text = get_ocr_from_pdf_bytes(textract, pdf_bytes)

    prompt = f"""
        <context>{context}</context>
        <ocr>{ocr_text}</ocr>
        <fields>{json.dumps(extraction_fields)}</fields>
    """.strip()

    try:
        hash = sha256(prompt.encode())
        cache = llm_cache.get(hash)
        if cache:
            print("Using prompt cache")
            return cache

        response = call_bedrock_agent(prompt, pdf_bytes)
        llm_cache[hash] = response
        return response
    except Exception as e:
        print(f"Error calling Bedrock Agent: {e}")
        return {}
    finally:
        print("Done.")


def call_bedrock_agent(prompt, pdf_bytes):
    print("Calling AWS Bedrock Agent...")
    response = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId="streamlit-localhost",
        inputText=prompt,
        sessionState={
            'files': [
                {
                    'name': 'user_input',
                    'source': {
                        'byteContent': {
                            'data': pdf_bytes,
                            'mediaType': "application/pdf",
                        },
                        'sourceType': 'BYTE_CONTENT'
                    },
                    'useCase': 'CHAT'
                },
            ]
        }
    )
    completion = response["completion"]
    return parse_bedrock_completion(completion)

def parse_bedrock_completion(response):
    for event in response:
        chunk = event.get('chunk')
        if not chunk:
            continue
        byte_data = chunk.get('bytes')
        if not byte_data:
            continue
        try:
            decoded = byte_data.decode('utf-8')
            return json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise Exception("Error decoding or parsing chunk")
    return None
