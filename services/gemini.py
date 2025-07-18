# services/gemini.py

import os
import json
import asyncio
from typing import Dict, Tuple, Any, List
import logging
from datetime import datetime

# New imports for direct PDF and Gemini handling
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.gemini import RESUME_EXTRACTION_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

# Configure the Gemini client
genai.configure(api_key=GEMINI_API_KEY)


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


def extract_pinecone_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts key information from the JSON for Pinecone metadata. (No changes needed here)"""
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

async def extract_resume_json_with_gemini(pdf_path: str) -> Dict[str, Any]:
    """
    Extracts resume content by sending PDF page images to Gemini Vision.
    This function replaces the xerox-based extraction.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        A dictionary containing the structured resume data.
    """
    # Use the centralized prompt for resume extraction
    system_prompt = RESUME_EXTRACTION_PROMPT
    
    try:
        logger.info(f"Initializing Gemini model: {GEMINI_MODEL}")
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        logger.info(f"Converting PDF '{pdf_path}' to images...")
        image_parts = get_pdf_image_parts(pdf_path)
        
        # Combine the text prompt with the list of page images
        prompt_parts = [system_prompt] + image_parts
        
        logger.info(f"Sending {len(image_parts)} pages to Gemini for processing...")
        # Use generate_content_async for non-blocking I/O in FastAPI
        response = await model.generate_content_async(prompt_parts)

        print(f"\n\nReceived response from Gemini: {response}\n\n")
        
        json_string = response.text

        usage_metadata_proto = response.usage_metadata
        usage_metadata = {
            "prompt_token_count": int(usage_metadata_proto.prompt_token_count),
            "candidates_token_count": int(usage_metadata_proto.candidates_token_count),
            "total_token_count": int(usage_metadata_proto.total_token_count)
        }
        logger.info(f"Gemini API Usage: {usage_metadata}")
        
        # Clean up the string to ensure it's valid JSON
        if json_string.strip().startswith("```json"):
            json_string = json_string.strip()[7:-4].strip()
        
        try:
            parsed_json = json.loads(json_string)
            logger.info("Successfully parsed JSON response from Gemini.")
            return parsed_json, usage_metadata
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini. Raw output: {json_string}")
            raise Exception(f"JSON parsing failed: {e}. The model did not return valid JSON.")

    except Exception as e:
        logger.error(f"Failed during Gemini API call: {str(e)}")
        raise

async def extract_resume_data(pdf_path: str) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """
    Orchestrates the new resume processing workflow.
    
    Returns:
        A tuple containing:
        - pinecone_metadata (Dict): Rich metadata for Pinecone.
        - markdown_content (str): The full resume content in markdown.
        - firestore_data (Dict): Data to be stored in Firestore, including usage metadata.
    """
    try:
        # Step 1: Unpack the new tuple returned by our Gemini function
        parsed_json, usage_metadata = await extract_resume_json_with_gemini(pdf_path)
        
        # Step 2: Extract rich metadata for Pinecone (no change)
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