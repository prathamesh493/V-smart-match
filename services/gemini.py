import os
import json
import asyncio
from typing import Dict, Tuple, Any
from pyzerox import zerox
from app.config import GEMINI_API_KEY, GEMINI_MODEL

# Set Gemini API key for zerox
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

async def extract_resume_with_zerox(pdf_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract resume content in markdown format using zerox library
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple containing metadata dictionary and markdown formatted content
    """
    try:
        # Define the system prompt for resume parsing
        custom_system_prompt = """
        You are a specialized AI for parsing resumes. Extract the complete content of this resume and format it in clean,
        well-structured markdown. Include all information such as:
        - Contact details and personal information
        - Professional summary/objective
        - Education history
        - Work experience
        - Skills
        - Projects
        - Certifications
        - Languages
        - Any other relevant sections
        
        Maintain the original structure but convert it to proper markdown format with appropriate headings,
        bullet points, and formatting.
        """
        
        # Define model string in zerox format
        model = f"gemini/{GEMINI_MODEL}"
        
        # Process the PDF with zerox
        result = await zerox(
            file_path=pdf_path,
            model=model,
            custom_system_prompt=custom_system_prompt,
            select_pages=None,  # Process all pages
            output_dir=None  # Don't save to file
        )
        
        # Extract the text content from all pages and join them
        markdown_content = ""
        if hasattr(result, 'pages') and result.pages:
            markdown_content = "\n\n".join([page.content for page in result.pages])
        
        # Create metadata dictionary
        metadata = {
            "completion_time": getattr(result, 'completion_time', None),
            "file_name": getattr(result, 'file_name', None),
            "input_tokens": getattr(result, 'input_tokens', None),
            "output_tokens": getattr(result, 'output_tokens', None),
            "page_count": len(getattr(result, 'pages', [])),
        }
        
        return metadata, markdown_content
    except Exception as e:
        raise Exception(f"Failed to extract resume with zerox: {str(e)}")

async def extract_resume_data(pdf_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Process a resume PDF file:
    1. Use zerox to extract content in markdown format
    2. Return parsed data dict and markdown text
    
    Returns:
        Tuple with parsed data dict and markdown content
    """
    try:
        # Extract markdown using zerox
        metadata, markdown_content = await extract_resume_with_zerox(pdf_path)
        
        # Create a structured parsed data dictionary
        parsed_data = {
            "extracted_content": markdown_content,
            "format": "markdown",
            "metadata": metadata
        }
        
        return parsed_data, markdown_content
    except Exception as e:
        raise Exception(f"Failed to process resume: {str(e)}")