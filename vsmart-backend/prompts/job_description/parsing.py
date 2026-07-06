"""
Job description parsing prompt for AI service.
"""

JOB_DESCRIPTION_PARSING_PROMPT = """
Parse the job description content and return ONLY the formatted markdown output. Do not include any introductory text, explanations, or commentary.

Extract and format the complete job description content in clean, well-structured markdown. Include all information such as:
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

Return only the markdown-formatted job description content without any additional text.
"""
