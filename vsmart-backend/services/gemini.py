# services/gemini.py

import os
import json
import asyncio
from typing import Dict, Tuple, Any, List
import logging
from datetime import datetime

# New imports for LangChain and PDF handling
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
import fitz  # PyMuPDF
from PIL import Image
import io
import base64

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.gemini import RESUME_EXTRACTION_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

# Configure LangSmith if enabled
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "vsmart-resume-extraction")
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


@traceable(name="convert_json_to_markdown")
def convert_json_to_markdown(data: Dict[str, Any]) -> str:
    """Converts the parsed resume JSON into a clean markdown string. (No changes needed here)"""
    markdown_parts = []

    # Personal Info
    personal_info = data.get("personal_info", {})
    if personal_info and personal_info.get('name'):
        markdown_parts.append(f"# {personal_info.get('name', 'N/A')}")
        details = []
        if personal_info.get('email'): details.append(f"- **Email:** {personal_info.get('email')}")
        if personal_info.get('phone'): details.append(f"- **Phone:** {personal_info.get('phone')}")
        if personal_info.get('location'): details.append(f"- **Location:** {personal_info.get('location')}")
        if personal_info.get('linkedin'): details.append(f"- **LinkedIn:** {personal_info.get('linkedin')}")
        if personal_info.get('github'): details.append(f"- **GitHub:** {personal_info.get('github')}")
        markdown_parts.append("\n".join(details))

    # Summary
    if data.get("summary"):
        markdown_parts.append(f"## Professional Summary\n\n{data['summary']}")

    # Work Experience
    if data.get("work_experience"):
        markdown_parts.append("## Work Experience")
        for job in data["work_experience"]:
            markdown_parts.append(f"### {job.get('job_title')} at {job.get('company')}")
            markdown_parts.append(f"*{job.get('start_date', '')} - {job.get('end_date', 'Present')} | {job.get('location', '')}*")
            if job.get("responsibilities"):
                responsibilities = "\n".join([f"- {desc}" for desc in job["responsibilities"]])
                markdown_parts.append(responsibilities)
            markdown_parts.append("")

    # Education
    if data.get("education"):
        markdown_parts.append("## Education")
        for edu in data["education"]:
            markdown_parts.append(f"### {edu.get('degree')}")
            markdown_parts.append(f"*{edu.get('university')} | {edu.get('graduation_date')}*")
            markdown_parts.append("")

    # Skills
    if data.get("skills"):
        markdown_parts.append("## Skills")
        skills_md = []
        for category, skill_list in data["skills"].items():
            if isinstance(skill_list, list) and skill_list:
                cat_name = category.replace('_', ' ').title()
                skills_md.append(f"**{cat_name}:** {', '.join(skill_list)}")
        markdown_parts.append("\n".join(skills_md))
        
    # Projects
    if data.get("projects"):
        markdown_parts.append("## Projects")
        for project in data["projects"]:
            markdown_parts.append(f"### {project.get('name')}")
            if project.get('description'): markdown_parts.append(project.get('description'))
            if project.get('technologies'): markdown_parts.append(f"**Technologies:** {', '.join(project.get('technologies'))}")
            if project.get('link'): markdown_parts.append(f"**Link:** {project.get('link')}")
            markdown_parts.append("")
    
    # Certifications
    if data.get("certifications"):
        markdown_parts.append("## Certifications")
        for cert in data["certifications"]:
            org = f" from {cert.get('issuing_organization')}" if cert.get('issuing_organization') else ""
            markdown_parts.append(f"- **{cert.get('name')}**{org} ({cert.get('date', 'N/A')})")

    return "\n\n".join(markdown_parts)


@traceable(name="extract_pinecone_metadata")
def extract_pinecone_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts key information from the JSON for Pinecone metadata."""
    metadata = {}
    personal_info = data.get("personal_info", {})
    metadata['name'] = personal_info.get('name')
    metadata['email'] = personal_info.get('email')
    metadata['location'] = personal_info.get('location')

    skills_data = data.get("skills", {})
    all_skills = []
    if skills_data:
        for key, value in skills_data.items():
            if isinstance(value, list):
                all_skills.extend(value)
    
    metadata['skills'] = list(set([s.lower() for s in all_skills])) # Lowercase for consistent filtering
    
    return {k: v for k, v in metadata.items() if v is not None and v}


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

@traceable(name="extract_resume_json_with_gemini")
async def extract_resume_json_with_gemini(pdf_path: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extracts resume content by sending PDF page images to Gemini Vision using LangChain.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        A tuple containing:
        - Dictionary with structured resume data
        - Dictionary with usage metadata
    """
    # Use the centralized prompt for resume extraction
    system_prompt = RESUME_EXTRACTION_PROMPT
    
    try:
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
            # You can add custom metadata to the trace
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
        
        logger.info(f"Received response from LangChain Gemini: {response}")
        
        json_string = response.content
        
        # For LangChain, we don't have direct access to usage metadata
        # You might need to implement usage tracking separately if needed
        usage_metadata = {
            "prompt_token_count": 0,  # Not directly available in LangChain
            "candidates_token_count": 0,  # Not directly available in LangChain
            "total_token_count": 0,  # Not directly available in LangChain
            "provider": "langchain-google-genai",
            "model": GEMINI_MODEL,
            "langsmith_tracing_enabled": LANGSMITH_TRACING,
            "langsmith_project": LANGSMITH_PROJECT if LANGSMITH_TRACING else None,
            "num_pages_processed": len(image_parts)
        }
        logger.info(f"Using LangChain - detailed usage metadata not available, but tracking: {usage_metadata}")
        
        # Clean up the string to ensure it's valid JSON
        if json_string.strip().startswith("```json"):
            json_string = json_string.strip()[7:-4].strip()
        
        try:
            parsed_json = json.loads(json_string)
            logger.info("Successfully parsed JSON response from LangChain Gemini.")
            return parsed_json, usage_metadata
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LangChain Gemini. Raw output: {json_string}")
            raise Exception(f"JSON parsing failed: {e}. The model did not return valid JSON.")

    except Exception as e:
        logger.error(f"Failed during LangChain Gemini API call: {str(e)}")
        raise

@traceable(name="extract_resume_data")
async def extract_resume_data(pdf_path: str) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """
    Orchestrates the new resume processing workflow.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        A tuple containing:
        - pinecone_metadata (Dict): Rich metadata for Pinecone.
        - markdown_content (str): The full resume content in markdown.
        - firestore_data (Dict): Data to be stored in Firestore, including usage metadata.
    """
    try:
        # Step 1: Unpack the new tuple returned by our Gemini function
        parsed_json, usage_metadata = await extract_resume_json_with_gemini(pdf_path)
        
        # Step 2: Extract rich metadata for Pinecone
        pinecone_metadata = extract_pinecone_metadata(parsed_json)
        
        # Step 3: Convert the JSON back to markdown (no change)
        markdown_content = convert_json_to_markdown(parsed_json)

        # Step 4: Prepare the data packet for Firestore, now including usage stats
        firestore_data = {
            "extracted_content": markdown_content,
            "format": "markdown",
            "metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "model_used": GEMINI_MODEL,
                "usage": usage_metadata  # <-- We add the usage data here
            },
            "source_json": parsed_json
        }
        
        return pinecone_metadata, markdown_content, firestore_data

    except Exception as e:
        raise Exception(f"Failed to process resume: {str(e)}")