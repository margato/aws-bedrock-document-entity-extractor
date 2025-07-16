
import hashlib
from io import BytesIO
import io
from cachetools import LRUCache
from pdf2image import convert_from_bytes
from botocore.exceptions import ClientError
from PIL import Image

ocr_cache = LRUCache(maxsize=5)
pdf_convertion_cache = LRUCache(maxsize=5)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def get_ocr_from_pdf_bytes(textract_client, pdf_bytes: bytes) -> str:
    hash = sha256(pdf_bytes)
    cache = ocr_cache.get(hash)
    if cache:
        print("Using OCR cache")
        return cache

    print("Reading PDF")
    try:
        images = convert_from_bytes(pdf_bytes)
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return ""

    ocr_lines = []
    for img in images:
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        try:
            response = textract_client.detect_document_text(
                Document={'Bytes': buffer.read()}
            )
            lines = [
                item["Text"]
                for item in response.get("Blocks", [])
                if item["BlockType"] == "LINE"
            ]
            ocr_lines.extend(lines)
        except ClientError as e:
            print(f"Textract error: {e}")
            continue

    text = "\n".join(ocr_lines)
    ocr_cache[hash] = text
    return text

def convert_to_pdf_if_needed(document_bytes: bytes, media_type: str) -> bytes:
    if media_type.lower() == "application/pdf":
        return document_bytes
    
    hash = sha256(bytes)
    cache = pdf_convertion_cache.get(hash)

    if cache:
        print("Using PDF conversion cache")
        return cache

    print("Converting to PDF...")
    try:
        img = Image.open(io.BytesIO(document_bytes))
        pdf_bytes_io = io.BytesIO()
        img.save(pdf_bytes_io, format="PDF")
        pdf_bytes_io.seek(0)
        bytes = pdf_bytes_io.read()
        pdf_convertion_cache[hash] = bytes
    except Exception:
        raise Exception("Could not convert image to PDF")