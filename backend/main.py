# backend/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from backend.services.translation_service import TranslationService, create_translation_chain
from backend.utils.language_map import language_map
import logging
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="File Translation API",
    description="A scalable API for translating file content into multiple languages using LangChain and OpenAI.",
    version="1.0.0",
)

translation_chain = create_translation_chain(max_chunk_size=500)

@app.post("/translate-file/")
async def translate_file(
    file: UploadFile = File(...),
    target_language: str = Form(...),  # Use Form instead of Query
) -> Dict[str, str]:
    """Translate the contents of a file (PDF, HTML, PPT, or Text)."""
    logger.info(f"Received file: {file.filename}, target_language: {target_language}")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension == 'pdf':
        logger.info(f"Processing PDF file: {file.filename}")
        original_text = await TranslationService.extract_text_from_pdf(file)
    elif file_extension == 'html':
        logger.info(f"Processing HTML file: {file.filename}")
        original_text = await TranslationService.extract_text_from_html(file)
    elif file_extension in ['ppt', 'pptx']:
        logger.info(f"Processing PPT file: {file.filename}")
        original_text = await TranslationService.extract_text_from_ppt(file)
    elif file_extension == 'txt':
        logger.info(f"Processing Text file: {file.filename}")
        original_text = await TranslationService.extract_text_from_txt(file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if not original_text.strip():
        raise HTTPException(status_code=400, detail="No text found in file")

    try:
        translated_text = translation_chain.invoke({
            "text": original_text,
            "target_language": target_language
        })
    except Exception as e:
        logger.error(f"LangChain translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

    return JSONResponse({
        "original_text": original_text,
        "translated_text": translated_text,
        "target_language": language_map.get(target_language, "Unknown Language")
    })

@app.get("/")
async def root() -> Dict[str, str]:
    """Welcome endpoint for the API."""
    return {"message": "Welcome to the Translation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)