# backend/services/translation_service.py
from typing import List
from fastapi import UploadFile, HTTPException
from openai import OpenAI
from langchain_core.runnables import RunnableLambda, RunnableSequence
from dotenv import load_dotenv
import logging
import textwrap
import os
from backend.utils.text_extraction import extract_text_from_pdf, extract_text_from_ppt, extract_text_from_html, extract_text_from_txt

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify and initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not found. Ensure it is set in the .env file.")
client = OpenAI(api_key=api_key)

class TranslationService:
    @staticmethod
    async def extract_text_from_pdf(pdf_file: UploadFile) -> str:
        return await extract_text_from_pdf(pdf_file)

    @staticmethod
    async def extract_text_from_ppt(ppt_file: UploadFile) -> str:
        return await extract_text_from_ppt(ppt_file)

    @staticmethod
    async def extract_text_from_html(html_file: UploadFile) -> str:
        return await extract_text_from_html(html_file)

    @staticmethod
    async def extract_text_from_txt(txt_file: UploadFile) -> str:
        return await extract_text_from_txt(txt_file)

    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 500) -> List[str]:
        """Split text into smaller chunks to handle API limitations."""
        logger.info("Chunking text for translation")
        return textwrap.wrap(text, max_chunk_size, break_long_words=False, replace_whitespace=False)

    @staticmethod
    def translate_with_openai(text: str, target_language: str) -> str:
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system", 
                    "content": f"You are a professional translator, and you will translate to {target_language}."
                }, {
                    "role": "user", 
                    "content": prompt
                }],
                max_tokens=1000,
                temperature=0.3
            )
            translated_text = response.choices[0].message.content
            return translated_text
        except Exception as e:
            raise Exception(f"Translation failed: {e}")

def create_translation_chain(max_chunk_size: int = 500) -> RunnableSequence:
    """Create a LangChain workflow for translation."""
    chunk_text_func = RunnableLambda(
        lambda inputs: {
            "chunks": TranslationService.chunk_text(inputs["text"], max_chunk_size),
            "target_language": inputs["target_language"]
        }
    )

    translate_chunk_func = RunnableLambda(
        lambda inputs: {
            "translated_chunks": [
                TranslationService.translate_with_openai(chunk, inputs["target_language"])
                for chunk in inputs["chunks"]
            ],
            "target_language": inputs["target_language"]
        }
    )

    join_chunks_func = RunnableLambda(
        lambda inputs: " ".join(inputs["translated_chunks"])
    )

    chain = chunk_text_func | translate_chunk_func | join_chunks_func
    return chain