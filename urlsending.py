from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

app = FastAPI()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expected Bearer token for authentication
EXPECTED_TOKEN = "5aa05ad358e859e92978582cde20423149f28beb49da7a2bbb487afa8fce1be8"

# ----- Request/Response Models -----
class QuestionRequest(BaseModel):
    documents: str
    questions: List[str]

class AnswerResponse(BaseModel):
    answers: List[str]

# ----- Token Verifier -----
def verify_token(authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid format")
    
    token = authorization.split("Bearer ")[-1]
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Bearer token")

# ----- Placeholder Answer Generator -----
async def process_qa_request(document_url: str, questions: List[str]) -> List[str]:
    """
    Simulated processing function — replace with real QnA logic.
    """
    logger.info(f"Processing {len(questions)} questions for document at {document_url}")
    
    # Simulated processing delay
    import time
    time.sleep(1)

    # Simulated answer generation
    example_answers = [
        f"Sample answer for: {q}" for q in questions
    ]

    logger.info("Successfully generated answers")
    return example_answers

# ----- Endpoint -----
@app.post("/hackrx/run", response_model=AnswerResponse)
async def ask_questions(
    request: QuestionRequest,
    authorization: str = Depends(verify_token)
):
    try:
        logger.info(f"Received request with {len(request.questions)} questions")

        # Basic validation
        if not request.documents.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid document URL")
        if not request.questions:
            raise HTTPException(status_code=400, detail="Questions list is empty")

        # Process questions
        answer_list = await process_qa_request(request.documents, request.questions)

        return {"answers": answer_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ----- For Local Testing -----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
