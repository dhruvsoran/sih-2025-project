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
        self.admins_file = os.path.join(self.data_dir, 'admins.json')
        
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
            
        if not os.path.exists(self.admins_file):
            self._save_json(self.admins_file, [])
    
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
        """Generate comprehensive realistic internship opportunities"""
        return [
            # Technology & IT Sector
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
                'id': 'INT004',
                'title': 'AI Research Assistant',
                'organization': 'Centre for Development of Advanced Computing',
                'sector': 'Technology',
                'location': 'Bangalore',
                'duration': '8 months',
                'stipend': 25000,
                'required_skills': ['Machine Learning', 'Python', 'Research', 'Mathematics'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in artificial intelligence research projects and algorithm development.',
                'capacity': 15,
                'affirmative_action_required': True
            },
            {
                'id': 'INT005',
                'title': 'Software Development Intern',
                'organization': 'National Informatics Centre',
                'sector': 'Technology',
                'location': 'Pune',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Java', 'JavaScript', 'Database Management', 'Web Development'],
                'education_requirement': 'undergraduate',
                'description': 'Develop government web applications and digital services.',
                'capacity': 40,
                'affirmative_action_required': True
            },
            
            # Healthcare Sector
            {
                'id': 'INT006',
                'title': 'Healthcare Analytics Intern',
                'organization': 'All Institute of Medical Sciences',
                'sector': 'Healthcare',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 16000,
                'required_skills': ['Healthcare', 'Data Analysis', 'Medical Research', 'Statistics'],
                'education_requirement': 'undergraduate',
                'description': 'Support healthcare data analysis and medical research projects.',
                'capacity': 40,
                'affirmative_action_required': True
            },
            {
                'id': 'INT007',
                'title': 'Public Health Research Intern',
                'organization': 'National Centre for Disease Control',
                'sector': 'Healthcare',
                'location': 'Chennai',
                'duration': '8 months',
                'stipend': 14000,
                'required_skills': ['Public Health', 'Epidemiology', 'Research', 'Data Collection'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in disease surveillance and public health research programs.',
                'capacity': 25,
                'affirmative_action_required': True
            },
            {
                'id': 'INT008',
                'title': 'Medical Technology Intern',
                'organization': 'Indian Council of Medical Research',
                'sector': 'Healthcare',
                'location': 'Mumbai',
                'duration': '6 months',
                'stipend': 18000,
                'required_skills': ['Biomedical Engineering', 'Medical Devices', 'Research', 'Technology'],
                'education_requirement': 'undergraduate',
                'description': 'Support medical technology development and innovation projects.',
                'capacity': 20,
                'affirmative_action_required': False
            },
            
            # Finance & Banking
            {
                'id': 'INT009',
                'title': 'Financial Analysis Intern',
                'organization': 'Reserve Bank of India',
                'sector': 'Finance & Banking',
                'location': 'Mumbai',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Financial Analysis', 'Economics', 'Excel', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in economic research and financial market analysis.',
                'capacity': 25,
                'affirmative_action_required': False
            },
            {
                'id': 'INT010',
                'title': 'Banking Operations Intern',
                'organization': 'State Bank of India',
                'sector': 'Finance & Banking',
                'location': 'Kolkata',
                'duration': '4 months',
                'stipend': 12000,
                'required_skills': ['Banking Operations', 'Customer Service', 'Documentation', 'Finance'],
                'education_requirement': 'undergraduate',
                'description': 'Learn banking operations and customer service in public sector banking.',
                'capacity': 60,
                'affirmative_action_required': True
            },
            {
                'id': 'INT011',
                'title': 'Investment Research Intern',
                'organization': 'Securities and Exchange Board of India',
                'sector': 'Finance & Banking',
                'location': 'Mumbai',
                'duration': '6 months',
                'stipend': 22000,
                'required_skills': ['Investment Analysis', 'Capital Markets', 'Research', 'Excel'],
                'education_requirement': 'undergraduate',
                'description': 'Research market trends and support investment regulation activities.',
                'capacity': 15,
                'affirmative_action_required': False
            },
            
            # Education
            {
                'id': 'INT012',
                'title': 'Education Technology Intern',
                'organization': 'Ministry of Education',
                'sector': 'Education',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 15000,
                'required_skills': ['Education Technology', 'Content Development', 'Learning Design', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Develop educational content and support digital learning initiatives.',
                'capacity': 45,
                'affirmative_action_required': True
            },
            {
                'id': 'INT013',
                'title': 'Research Assistant - Higher Education',
                'organization': 'University Grants Commission',
                'sector': 'Education',
                'location': 'Bangalore',
                'duration': '8 months',
                'stipend': 16000,
                'required_skills': ['Research', 'Academic Writing', 'Data Analysis', 'Higher Education'],
                'education_requirement': 'undergraduate',
                'description': 'Support research in higher education policy and development.',
                'capacity': 30,
                'affirmative_action_required': True
            },
            {
                'id': 'INT014',
                'title': 'Skill Development Program Intern',
                'organization': 'Ministry of Skill Development',
                'sector': 'Education',
                'location': 'Bhopal',
                'duration': '6 months',
                'stipend': 13000,
                'required_skills': ['Training Design', 'Program Management', 'Documentation', 'Communication'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in designing and implementing skill development programs.',
                'capacity': 50,
                'affirmative_action_required': True
            },
            
            # Agriculture & Rural Development
            {
                'id': 'INT015',
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
                'id': 'INT016',
                'title': 'Agricultural Research Intern',
                'organization': 'Indian Agricultural Research Institute',
                'sector': 'Agriculture',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 14000,
                'required_skills': ['Agriculture', 'Research', 'Data Collection', 'Laboratory Skills'],
                'education_requirement': 'undergraduate',
                'description': 'Support agricultural research and crop development studies.',
                'capacity': 35,
                'affirmative_action_required': True
            },
            {
                'id': 'INT017',
                'title': 'Farm Technology Intern',
                'organization': 'Central Institute of Agricultural Engineering',
                'sector': 'Agriculture',
                'location': 'Chandigarh',
                'duration': '6 months',
                'stipend': 15000,
                'required_skills': ['Agricultural Technology', 'Engineering', 'Innovation', 'Field Work'],
                'education_requirement': 'undergraduate',
                'description': 'Work on farm mechanization and agricultural technology projects.',
                'capacity': 25,
                'affirmative_action_required': True
            },
            
            # Environment & Climate
            {
                'id': 'INT018',
                'title': 'Environmental Policy Intern',
                'organization': 'Ministry of Environment and Forests',
                'sector': 'Environment',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 14000,
                'required_skills': ['Environmental Science', 'Policy Research', 'Documentation', 'GIS'],
                'education_requirement': 'undergraduate',
                'description': 'Research and develop environmental policies and sustainability initiatives.',
                'capacity': 35,
                'affirmative_action_required': True
            },
            {
                'id': 'INT019',
                'title': 'Climate Change Research Intern',
                'organization': 'National Environmental Engineering Research Institute',
                'sector': 'Environment',
                'location': 'Pune',
                'duration': '8 months',
                'stipend': 16000,
                'required_skills': ['Climate Science', 'Research', 'Data Analysis', 'Environmental Monitoring'],
                'education_requirement': 'undergraduate',
                'description': 'Study climate change impacts and adaptation strategies.',
                'capacity': 20,
                'affirmative_action_required': True
            },
            {
                'id': 'INT020',
                'title': 'Wildlife Conservation Intern',
                'organization': 'Wildlife Institute of India',
                'sector': 'Environment',
                'location': 'Dehradun',
                'duration': '6 months',
                'stipend': 13000,
                'required_skills': ['Wildlife Biology', 'Conservation', 'Field Research', 'Photography'],
                'education_requirement': 'undergraduate',
                'description': 'Support wildlife conservation research and habitat protection programs.',
                'capacity': 30,
                'affirmative_action_required': True
            },
            
            # Defence & Security
            {
                'id': 'INT021',
                'title': 'Defence Research Intern',
                'organization': 'Defence Research and Development Organisation',
                'sector': 'Defence',
                'location': 'Bangalore',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Engineering', 'Research', 'Technology', 'Innovation'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in defence technology research and development projects.',
                'capacity': 25,
                'affirmative_action_required': False
            },
            {
                'id': 'INT022',
                'title': 'Border Security Technology Intern',
                'organization': 'Border Security Force',
                'sector': 'Defence',
                'location': 'New Delhi',
                'duration': '4 months',
                'stipend': 18000,
                'required_skills': ['Security Technology', 'Surveillance', 'Electronics', 'Communication'],
                'education_requirement': 'undergraduate',
                'description': 'Work on border security technology and surveillance systems.',
                'capacity': 20,
                'affirmative_action_required': True
            },
            
            # Space & Aerospace
            {
                'id': 'INT023',
                'title': 'Satellite Technology Intern',
                'organization': 'Indian Space Research Organisation',
                'sector': 'Space & Aerospace',
                'location': 'Bangalore',
                'duration': '8 months',
                'stipend': 25000,
                'required_skills': ['Aerospace Engineering', 'Satellite Technology', 'Programming', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Support satellite development and space technology projects.',
                'capacity': 15,
                'affirmative_action_required': False
            },
            {
                'id': 'INT024',
                'title': 'Space Applications Intern',
                'organization': 'National Remote Sensing Centre',
                'sector': 'Space & Aerospace',
                'location': 'Hyderabad',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Remote Sensing', 'GIS', 'Data Analysis', 'Programming'],
                'education_requirement': 'undergraduate',
                'description': 'Work on satellite data applications for earth observation.',
                'capacity': 25,
                'affirmative_action_required': True
            },
            
            # Transportation
            {
                'id': 'INT025',
                'title': 'Railway Engineering Intern',
                'organization': 'Indian Railways',
                'sector': 'Transportation',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 16000,
                'required_skills': ['Mechanical Engineering', 'Railway Systems', 'Maintenance', 'Safety'],
                'education_requirement': 'undergraduate',
                'description': 'Support railway engineering and infrastructure development.',
                'capacity': 50,
                'affirmative_action_required': True
            },
            {
                'id': 'INT026',
                'title': 'Smart Transportation Intern',
                'organization': 'Ministry of Road Transport and Highways',
                'sector': 'Transportation',
                'location': 'Mumbai',
                'duration': '6 months',
                'stipend': 18000,
                'required_skills': ['Transportation Planning', 'Smart Systems', 'Data Analysis', 'Urban Planning'],
                'education_requirement': 'undergraduate',
                'description': 'Work on smart transportation systems and traffic management.',
                'capacity': 30,
                'affirmative_action_required': False
            },
            
            # Tourism & Culture
            {
                'id': 'INT027',
                'title': 'Cultural Heritage Preservation Intern',
                'organization': 'Archaeological Survey of India',
                'sector': 'Tourism & Culture',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 12000,
                'required_skills': ['Archaeology', 'History', 'Documentation', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Support cultural heritage preservation and archaeological projects.',
                'capacity': 40,
                'affirmative_action_required': True
            },
            {
                'id': 'INT028',
                'title': 'Digital Tourism Promotion Intern',
                'organization': 'Ministry of Tourism',
                'sector': 'Tourism & Culture',
                'location': 'Goa',
                'duration': '4 months',
                'stipend': 15000,
                'required_skills': ['Digital Marketing', 'Tourism', 'Content Creation', 'Social Media'],
                'education_requirement': 'undergraduate',
                'description': 'Promote Indian tourism through digital marketing initiatives.',
                'capacity': 35,
                'affirmative_action_required': True
            },
            
            # Energy & Power
            {
                'id': 'INT029',
                'title': 'Renewable Energy Research Intern',
                'organization': 'Solar Energy Corporation of India',
                'sector': 'Energy',
                'location': 'Gurugram',
                'duration': '6 months',
                'stipend': 18000,
                'required_skills': ['Renewable Energy', 'Solar Technology', 'Research', 'Engineering'],
                'education_requirement': 'undergraduate',
                'description': 'Research renewable energy technologies and solar power systems.',
                'capacity': 30,
                'affirmative_action_required': True
            },
            {
                'id': 'INT030',
                'title': 'Power Grid Analytics Intern',
                'organization': 'Power Grid Corporation of India',
                'sector': 'Energy',
                'location': 'New Delhi',
                'duration': '6 months',
                'stipend': 20000,
                'required_skills': ['Power Systems', 'Data Analysis', 'Engineering', 'Grid Management'],
                'education_requirement': 'undergraduate',
                'description': 'Analyze power grid performance and optimization strategies.',
                'capacity': 25,
                'affirmative_action_required': False
            }
        ]
    
    def get_all_admins(self) -> List[Dict[str, Any]]:
        """Get all admin users"""
        return self._load_json(self.admins_file)
    
    def get_admin_by_email(self, email: str) -> Dict[str, Any] | None:
        """Get admin by email"""
        admins = self.get_all_admins()
        for admin in admins:
            if admin.get('email') == email:
                return admin
        return None
    
    def add_admin(self, admin_data: Dict[str, Any]):
        """Add a new admin user"""
        admins = self.get_all_admins()
        admins.append(admin_data)
        self._save_json(self.admins_file, admins)
