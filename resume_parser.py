import re
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Common technical skills to extract from resumes
TECHNICAL_SKILLS = [
    'python', 'java', 'javascript', 'c++', 'c', 'sql', 'html', 'css',
    'react', 'angular', 'node.js', 'django', 'flask', 'fastapi',
    'machine learning', 'deep learning', 'data analysis', 'data science',
    'artificial intelligence', 'ai', 'ml', 'nlp', 'natural language processing',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'excel', 'power bi', 'tableau', 'statistics', 'r programming',
    'aws', 'azure', 'cloud computing', 'docker', 'kubernetes', 'linux',
    'git', 'github', 'database management', 'mongodb', 'postgresql', 'mysql',
    'web development', 'frontend', 'backend', 'full stack', 'rest api',
    'cybersecurity', 'network security', 'ethical hacking', 'penetration testing',
    'digital marketing', 'seo', 'social media', 'content writing', 'copywriting',
    'project management', 'agile', 'scrum', 'jira', 'confluence',
    'figma', 'ui/ux', 'graphic design', 'photoshop', 'illustrator',
    'video editing', 'photography', 'content creation', 'social media marketing',
    'financial analysis', 'accounting', 'tally', 'gst', 'taxation',
    'research', 'academic writing', 'technical writing', 'report writing',
    'communication', 'leadership', 'team management', 'public speaking',
    'engineering', 'mechanical engineering', 'electrical engineering', 'civil engineering',
    'electronics', 'circuit design', 'vlsi', 'embedded systems', 'iot',
    'blockchain', 'web3', 'solidity', 'smart contracts',
    'devops', 'ci/cd', 'jenkins', 'terraform', 'ansible',
    'mobile app development', 'android', 'ios', 'flutter', 'react native',
    'sql', 'nosql', 'data engineering', 'etl', 'spark', 'hadoop',
    'mathematics', 'linear algebra', 'calculus', 'probability',
    'physics', 'chemistry', 'biology', 'biotechnology',
    'environmental science', 'gis', 'remote sensing', 'sustainability',
    'agriculture', 'food science', 'nutrition', 'public health',
    'education', 'teaching', 'curriculum design', 'learning management',
    'law', 'legal research', 'constitutional law', 'corporate law',
    'journalism', 'mass communication', 'public relations', 'media',
    'archaeology', 'history', 'museum studies', 'heritage management',
    'transportation', 'logistics', 'supply chain', 'operations management',
    'renewable energy', 'solar', 'wind', 'power systems', 'electrical grid',
    'aerospace', 'satellite', 'drone', 'robotics', 'automation',
    'telecommunications', '5g', 'networking', 'wireless',
    'healthcare', 'medical devices', 'biomedical', 'clinical research',
    'pharmaceutical', 'drug discovery', 'bioinformatics', 'genomics',
]

# Education keywords
EDUCATION_KEYWORDS = [
    'bachelor', 'master', 'phd', 'doctorate', 'b.tech', 'm.tech', 'b.sc', 'm.sc',
    'bca', 'mca', 'bba', 'mba', 'b.com', 'm.com', 'b.ed', 'm.ed',
    'undergraduate', 'postgraduate', 'diploma', 'degree', 'graduation',
    'university', 'institute', 'college', 'school'
]

# Experience keywords
EXPERIENCE_KEYWORDS = [
    'experience', 'worked', 'intern', 'internship', 'employment', 'job',
    'position', 'role', 'responsibilities', 'achievements', 'projects'
]


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    try:
        import docx
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""


def extract_skills(text: str) -> List[str]:
    """Extract technical skills from resume text."""
    text_lower = text.lower()
    found_skills = []
    
    for skill in TECHNICAL_SKILLS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            # Capitalize the skill for display
            found_skills.append(skill.title())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)
    
    return unique_skills[:15]  # Limit to 15 skills


def extract_education(text: str) -> str:
    """Extract education level from resume text."""
    text_lower = text.lower()
    
    if 'phd' in text_lower or 'doctorate' in text_lower:
        return 'phd'
    elif 'master' in text_lower or 'm.tech' in text_lower or 'm.sc' in text_lower or 'mba' in text_lower or 'mca' in text_lower:
        return 'master'
    elif 'bachelor' in text_lower or 'b.tech' in text_lower or 'b.sc' in text_lower or 'bca' in text_lower or 'bba' in text_lower:
        return 'bachelor'
    elif 'undergraduate' in text_lower:
        return 'undergraduate'
    elif 'diploma' in text_lower:
        return 'diploma'
    elif '12th' in text_lower or 'higher secondary' in text_lower:
        return '12th'
    elif 'high school' in text_lower or '10th' in text_lower:
        return 'high school'
    
    return 'undergraduate'  # Default


def extract_experience_years(text: str) -> str:
    """Extract experience level from resume text."""
    text_lower = text.lower()
    
    # Look for explicit experience mentions
    exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience'
    match = re.search(exp_pattern, text_lower)
    if match:
        years = int(match.group(1))
        if years >= 2:
            return '2+ years'
        elif years >= 1:
            return '1-2 years'
        else:
            return '6-12 months'
    
    # Check for internship mentions
    intern_count = text_lower.count('intern')
    if intern_count >= 2:
        return '0-6 months'
    elif intern_count >= 1:
        return 'fresher'
    
    # Check for project mentions
    project_count = text_lower.count('project')
    if project_count >= 3:
        return '0-6 months'
    
    return 'fresher'


def extract_interests(text: str, skills: List[str]) -> List[str]:
    """Derive interests from skills and resume content."""
    interest_mapping = {
        'Technology': ['python', 'java', 'javascript', 'react', 'node.js', 'django', 'flask',
                       'web development', 'frontend', 'backend', 'full stack', 'cloud computing',
                       'aws', 'azure', 'docker', 'kubernetes', 'devops', 'mobile app development'],
        'Research & Analytics': ['data analysis', 'data science', 'machine learning', 'deep learning',
                                 'research', 'statistics', 'mathematics', 'ai', 'ml', 'nlp'],
        'Healthcare': ['healthcare', 'medical devices', 'biomedical', 'clinical research',
                       'pharmaceutical', 'bioinformatics', 'public health'],
        'Finance & Banking': ['financial analysis', 'accounting', 'tally', 'gst', 'taxation',
                              'investment', 'banking', 'economics'],
        'Education': ['education', 'teaching', 'curriculum design', 'content development'],
        'Environment': ['environmental science', 'gis', 'remote sensing', 'sustainability',
                        'renewable energy', 'climate'],
        'Defence': ['cybersecurity', 'network security', 'electronics', 'embedded systems',
                    'robotics', 'automation', 'aerospace'],
        'Space & Aerospace': ['aerospace', 'satellite', 'drone', 'robotics', 'remote sensing'],
        'Agriculture': ['agriculture', 'food science', 'nutrition', 'biotechnology'],
        'Transportation': ['transportation', 'logistics', 'supply chain', 'operations management'],
        'Energy': ['renewable energy', 'solar', 'wind', 'power systems', 'electrical grid'],
        'Digital Marketing': ['digital marketing', 'seo', 'social media', 'content writing',
                              'content creation', 'social media marketing'],
    }
    
    text_lower = text.lower()
    matched_interests = []
    
    for interest, keywords in interest_mapping.items():
        for keyword in keywords:
            if keyword.lower() in text_lower or keyword.lower() in [s.lower() for s in skills]:
                if interest not in matched_interests:
                    matched_interests.append(interest)
                break
    
    return matched_interests[:5]  # Limit to 5 interests


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file and extract structured data.
    
    Args:
        file_path: Path to the resume file (PDF or DOCX)
    
    Returns:
        Dictionary with extracted information
    """
    # Extract text based on file type
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        text = extract_text_from_docx(file_path)
    else:
        return {'error': f'Unsupported file format: {ext}'}
    
    if not text.strip():
        return {'error': 'Could not extract text from the resume. The file may be image-based or corrupted.'}
    
    # Extract information
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience_years(text)
    interests = extract_interests(text, skills)
    
    # Extract name (simple heuristic - first line that's not too long)
    name = ""
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if line and len(line) < 50 and not any(kw in line.lower() for kw in EDUCATION_KEYWORDS + EXPERIENCE_KEYWORDS + ['@', 'email', 'phone', 'mobile', 'address']):
            name = line
            break
    
    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else ""
    
    # Extract phone
    phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group(0) if phone_match else ""
    
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'education': education,
        'experience': experience,
        'interests': interests,
        'raw_text': text[:2000],  # Limit raw text for storage
        'text_length': len(text)
    }
