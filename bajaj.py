from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
import os
import requests
from pathlib import Path

# Document parsers
import fitz  # PyMuPDF
import docx
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup

app = FastAPI()


# ----- Request/Response Models -----
class QueryRequest(BaseModel):
    documents: str
    questions: List[str]


class QueryResponse(BaseModel):
    answers: List[str]


# ----- Helper Functions -----
def download_file(url: str, dest: str):
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Download failed")
    with open(dest, 'wb') as f:
        f.write(r.content)


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        doc = fitz.open(file_path)
        return "\n".join([page.get_text() for page in doc])

    elif ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    elif ext == ".eml":
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    return BeautifulSoup(part.get_content(), 'html.parser').get_text()
                elif part.get_content_type() == 'text/plain':
                    return part.get_content()
        return msg.get_body(preferencelist=('plain')).get_content()

    else:
        raise Exception(f"Unsupported file format: {ext}")


# ----- Main Endpoint -----
@app.post("/hackrx/run", response_model=QueryResponse)
async def answer_questions(
    request_data: QueryRequest,
    authorization: str = Header(...)
):
    # Auth check
    expected_token = "Bearer 5aa05ad358e859e92978582cde20423149f28beb49da7a2bbb487afa8fce1be8"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    document_url = request_data.documents
    questions = request_data.questions

    try:
        file_ext = Path(document_url.split("?")[0]).suffix or ".pdf"
        file_path = f"temp_document{file_ext}"
        download_file(document_url, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

    try:
        document_text = extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)

    # Placeholder model answers (replace this with actual model call)
    answers = [
        f"Answer to '{q}': [Placeholder using extracted text of {len(document_text)} chars]"
        for q in questions
    ]

    return QueryResponse(answers=answers)
