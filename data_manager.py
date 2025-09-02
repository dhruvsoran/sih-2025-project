import json
import os
from typing import List, Dict, Any

class DataManager:
    """Manages data storage and retrieval using JSON files"""
    
    def __init__(self):
        self.data_dir = 'data'
        self.students_file = os.path.join(self.data_dir, 'students.json')
        self.internships_file = os.path.join(self.data_dir, 'internships.json')
        self.matches_file = os.path.join(self.data_dir, 'matches.json')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files with sample data if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with empty lists if they don't exist"""
        if not os.path.exists(self.students_file):
            self._save_json(self.students_file, [])
        
        if not os.path.exists(self.internships_file):
            self._save_json(self.internships_file, self._get_sample_internships())
        
        if not os.path.exists(self.matches_file):
            self._save_json(self.matches_file, [])
    
    def _load_json(self, filepath: str) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, filepath: str, data: List[Dict[str, Any]]):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students"""
        return self._load_json(self.students_file)
    
    def get_student(self, student_id: str) -> Dict[str, Any] | None:
        """Get a specific student by ID"""
        students = self.get_all_students()
        for student in students:
            if student.get('id') == student_id:
                return student
        return None
    
    def add_student(self, student_data: Dict[str, Any]):
        """Add a new student"""
        students = self.get_all_students()
        students.append(student_data)
        self._save_json(self.students_file, students)
    
    def get_all_internships(self) -> List[Dict[str, Any]]:
        """Get all internships"""
        return self._load_json(self.internships_file)
    
    def get_all_matches(self) -> List[Dict[str, Any]]:
        """Get all matches"""
        return self._load_json(self.matches_file)
    
    def add_match(self, match_data: Dict[str, Any]):
        """Add a new match result"""
        matches = self.get_all_matches()
        
        # Remove existing match for the same student
        matches = [m for m in matches if m.get('student_id') != match_data.get('student_id')]
        
        matches.append(match_data)
        self._save_json(self.matches_file, matches)
    
    def _get_sample_internships(self) -> List[Dict[str, Any]]:
        """Generate sample internship opportunities"""
        return [
            {
                'id': 'INT001',
                'title': 'Digital Marketing Intern',
                'organization': 'Ministry of Electronics and IT',
                'sector': 'Technology',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 15000,
                'required_skills': ['Digital Marketing', 'Social Media', 'Content Writing', 'Analytics'],
                'education_requirement': 'undergraduate',
                'description': 'Support digital initiatives and social media campaigns for government technology programs.',
                'capacity': 50,
                'affirmative_action_required': True
            },
            {
                'id': 'INT002',
                'title': 'Data Analytics Intern',
                'organization': 'National Sample Survey Office',
                'sector': 'Research & Analytics',
                'location': 'Mumbai',
                'duration': '6 months',
                'stipend': 18000,
                'required_skills': ['Python', 'Data Analysis', 'Statistics', 'Excel'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in analyzing survey data and generating insights for policy making.',
                'capacity': 30,
                'affirmative_action_required': False
            },
            {
                'id': 'INT003',
                'title': 'Rural Development Assistant',
                'organization': 'Ministry of Rural Development',
                'sector': 'Rural Development',
                'location': 'Bhopal',
                'duration': '8 months',
                'stipend': 12000,
                'required_skills': ['Project Management', 'Community Engagement', 'Documentation'],
                'education_requirement': 'undergraduate',
                'description': 'Support rural development programs and community outreach initiatives.',
                'capacity': 75,
                'affirmative_action_required': True
            },
            {
                'id': 'INT004',
                'title': 'Financial Analysis Intern',
                'organization': 'Reserve Bank of India',
                'sector': 'Finance & Banking',
                'location': 'Chennai',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Financial Analysis', 'Economics', 'Excel', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in economic research and financial market analysis.',
                'capacity': 25,
                'affirmative_action_required': False
            },
            {
                'id': 'INT005',
                'title': 'Healthcare Analytics Intern',
                'organization': 'All Institute of Medical Sciences',
                'sector': 'Healthcare',
                'location': 'Bangalore',
                'duration': '6 months',
                'stipend': 16000,
                'required_skills': ['Healthcare', 'Data Analysis', 'Medical Research', 'Statistics'],
                'education_requirement': 'undergraduate',
                'description': 'Support healthcare data analysis and medical research projects.',
                'capacity': 40,
                'affirmative_action_required': True
            },
            {
                'id': 'INT006',
                'title': 'Environmental Policy Intern',
                'organization': 'Ministry of Environment',
                'sector': 'Environment',
                'location': 'Pune',
                'duration': '6 months',
                'stipend': 14000,
                'required_skills': ['Environmental Science', 'Policy Research', 'Documentation', 'GIS'],
                'education_requirement': 'undergraduate',
                'description': 'Research and develop environmental policies and sustainability initiatives.',
                'capacity': 35,
                'affirmative_action_required': True
            },
            {
                'id': 'INT007',
                'title': 'Cybersecurity Analyst Intern',
                'organization': 'National Cyber Security Centre',
                'sector': 'Cybersecurity',
                'location': 'Hyderabad',
                'duration': '6 months',
                'stipend': 22000,
                'required_skills': ['Cybersecurity', 'Network Security', 'Ethical Hacking', 'Python'],
                'education_requirement': 'undergraduate',
                'description': 'Support cybersecurity initiatives and threat analysis.',
                'capacity': 20,
                'affirmative_action_required': False
            },
            {
                'id': 'INT008',
                'title': 'Education Technology Intern',
                'organization': 'Ministry of Education',
                'sector': 'Education',
                'location': 'Kolkata',
                'duration': '6 months',
                'stipend': 15000,
                'required_skills': ['Education Technology', 'Content Development', 'Learning Design', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Develop educational content and support digital learning initiatives.',
                'capacity': 45,
                'affirmative_action_required': True
            }
        ]
