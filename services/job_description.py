import os
import json
import asyncio
from typing import Dict, Tuple, Any
from pyzerox import zerox
from app.config import GEMINI_API_KEY, GEMINI_MODEL

# Set Gemini API key for zerox
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

async def extract_job_description_with_zerox(pdf_path: str) -> Tuple[Dict[str, Any], str]:
    """
    Extract job description content in markdown format using zerox library
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple containing metadata dictionary and markdown formatted content
    """
    try:
        # Define the system prompt for job description parsing
        custom_system_prompt = """
        You are a specialized AI for parsing job descriptions. Extract the complete content of this job description 
        and format it in clean, well-structured markdown. Include all information such as:
        - Job title and company name
        - Job summary/overview
        - Responsibilities
        - Requirements/qualifications
        - Skills (technical and soft skills)
        - Education requirements
        - Experience requirements
        - Benefits and perks
        - Location and work type (remote, hybrid, onsite)
        - Application process
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
        raise Exception(f"Failed to extract job description with zerox: {str(e)}")

async def extract_job_description_data(pdf_path: str, job_title: str = None, company: str = None) -> Tuple[Dict[str, Any], str]:
    """
    Process a job description PDF file:
    1. Use zerox to extract content in markdown format
    2. Return parsed data dict and markdown text
    
    Args:
        pdf_path: Path to the PDF file
        job_title: Optional job title to include in metadata
        company: Optional company name to include in metadata
        
    Returns:
        Tuple with parsed data dict and markdown content
    """
    try:
        # Extract markdown using zerox
        metadata, markdown_content = await extract_job_description_with_zerox(pdf_path)
        
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
        raise Exception(f"Failed to process job description: {str(e)}")