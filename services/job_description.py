import os
import json
import asyncio
from typing import Dict, Tuple, Any, List
import logging
from datetime import datetime

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
import fitz  # PyMuPDF
from PIL import Image
import io
import base64

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.job_description import JOB_DESCRIPTION_PARSING_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

# Configure LangSmith if enabled
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "vsmart-job-description-parsing")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"

if LANGSMITH_TRACING and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    logger.info(f"LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
else:
    logger.info("LangSmith tracing disabled")

# Initialize LangChain Gemini model
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

@traceable(name="get_pdf_image_parts")
def get_pdf_image_parts(pdf_path: str) -> List[Image.Image]:
    """
    Opens a PDF file and converts each page to a PIL Image object.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        image_parts = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # Render page to a pixmap (an image)
            pix = page.get_pixmap(dpi=150) # Higher DPI for better quality
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            image_parts.append(image)
        pdf_document.close()
        return image_parts
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise

@traceable(name="image_to_base64")
def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

@traceable(name="extract_job_description_with_langchain")
async def extract_job_description_with_langchain(pdf_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract job description content in markdown format using LangChain Gemini
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple containing metadata dictionary and markdown formatted content
    """
    try:
        # Use the centralized prompt for job description parsing
        system_prompt = JOB_DESCRIPTION_PARSING_PROMPT
        
        logger.info(f"Using LangChain Gemini model: {GEMINI_MODEL}")
        
        logger.info(f"Converting PDF '{pdf_path}' to images...")
        image_parts = get_pdf_image_parts(pdf_path)
        
        # Convert images to base64 for LangChain
        image_data = []
        for idx, image in enumerate(image_parts):
            base64_image = image_to_base64(image)
            image_data.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
        
        # Create message content with text and images
        message_content = [{"type": "text", "text": system_prompt}] + image_data
        
        # Create HumanMessage with multimodal content
        message = HumanMessage(content=message_content)
        
        logger.info(f"Sending {len(image_parts)} pages to Gemini for processing via LangChain...")
        
        # Add metadata for tracing
        if LANGSMITH_TRACING:
            from langsmith import trace
            with trace(name="gemini_api_call", metadata={
                "model": GEMINI_MODEL,
                "pdf_path": pdf_path,
                "num_pages": len(image_parts),
                "prompt_length": len(system_prompt)
            }):
                # Use LangChain to invoke the model
                response = await llm.ainvoke([message])
        else:
            # Use LangChain to invoke the model
            response = await llm.ainvoke([message])
        
        logger.info(f"Received response from LangChain Gemini")
        
        markdown_content = response.content
        
        # Create metadata dictionary
        metadata = {
            "completion_time": datetime.now().isoformat(),
            "file_name": os.path.basename(pdf_path),
            "input_tokens": 0,  # Not directly available in LangChain
            "output_tokens": 0,  # Not directly available in LangChain
            "page_count": len(image_parts),
            "provider": "langchain-google-genai",
            "model": GEMINI_MODEL,
            "langsmith_tracing_enabled": LANGSMITH_TRACING,
            "langsmith_project": LANGSMITH_PROJECT if LANGSMITH_TRACING else None,
        }
        
        # Try to extract job title and company if available in the content
        job_info = {}
        try:
            # Simple heuristic to extract job title and company
            # This is a basic implementation and might need refinement
            lines = markdown_content.split('\n')
            # Look for # or ## headings that might contain job title
            for line in lines[:10]:  # Check first 10 lines
                if line.startswith('# '):
                    job_info["job_title"] = line.replace('# ', '').strip()
                    break
                elif line.startswith('## '):
                    job_info["job_title"] = line.replace('## ', '').strip()
                    break
            
            # Look for company name in first few lines
            for line in lines[:15]:
                if "company:" in line.lower():
                    job_info["company"] = line.split(":", 1)[1].strip()
                    break
                elif "at " in line.lower() and job_info.get("job_title"):
                    possible_company = line.split("at ", 1)[1].strip()
                    if len(possible_company) < 50:  # Reasonable company name length
                        job_info["company"] = possible_company
                        break
        except Exception:
            # If extraction fails, we'll just skip this part
            pass
            
        metadata.update(job_info)
        
        return metadata, markdown_content
    except Exception as e:
        logger.error(f"Failed to extract job description with LangChain: {str(e)}")
        raise Exception(f"Failed to extract job description with LangChain: {str(e)}")

@traceable(name="extract_job_description_data")
async def extract_job_description_data(pdf_path: str, job_title: str = None, company: str = None) -> Tuple[Dict[str, Any], str]:
    """
    Process a job description PDF file:
    1. Use LangChain Gemini to extract content in markdown format
    2. Return parsed data dict and markdown text
    
    Args:
        pdf_path: Path to the PDF file
        job_title: Optional job title to include in metadata
        company: Optional company name to include in metadata
        
    Returns:
        Tuple with parsed data dict and markdown content
    """
    try:
        # Extract markdown using LangChain Gemini
        metadata, markdown_content = await extract_job_description_with_langchain(pdf_path)
        
        # Add manual metadata if provided
        if job_title:
            metadata["job_title"] = job_title
        if company:
            metadata["company"] = company
        
        # Create a structured parsed data dictionary
        parsed_data = {
            "extracted_content": markdown_content,
            "format": "markdown",
            "metadata": metadata,
            "job_title": metadata.get("job_title", job_title),
            "company": metadata.get("company", company)
        }
        
        return parsed_data, markdown_content
    except Exception as e:
        logger.error(f"Failed to process job description: {str(e)}")
        raise Exception(f"Failed to process job description: {str(e)}")