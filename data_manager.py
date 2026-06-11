import json
import os
import logging
import uuid
from typing import List, Dict, Any
from db_config import get_connection, init_db
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data storage and retrieval using SQLite database"""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        try:
            conn = get_connection()
            conn.close()
        except Exception:
            pass
        init_db()
        self._seed_internships_if_empty()
        self._seed_admin_if_empty()

    def _seed_admin_if_empty(self):
        """Create default admin account if no admins exist"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM admins")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    """INSERT INTO admins (id, name, email, password, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        'Prayaas Admin',
                        'admin@gmail.com',
                        generate_password_hash('199999'),
                        '2026-06-09'
                    )
                )
                conn.commit()
                logger.info("Default admin account created: admin@gmail.com")
        finally:
            conn.close()

    def _seed_internships_if_empty(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM internships")
            count = cursor.fetchone()[0]
            if count == 0:
                for internship in self._get_sample_internships():
                    cursor.execute(
                        """INSERT INTO internships
                           (id, title, organization, sector, location, duration,
                            stipend, required_skills, education_requirement,
                            description, capacity, affirmative_action_required, apply_url)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (
                            internship['id'], internship['title'],
                            internship['organization'], internship['sector'],
                            internship['location'], internship['duration'],
                            internship['stipend'],
                            json.dumps(internship['required_skills']),
                            internship['education_requirement'],
                            internship['description'], internship['capacity'],
                            1 if internship['affirmative_action_required'] else 0,
                            internship.get('apply_url', ''),
                        )
                    )
                conn.commit()
        finally:
            conn.close()

    def get_all_students(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d['skills'] = json.loads(d['skills']) if d['skills'] else []
                d['interests'] = json.loads(d['interests']) if d['interests'] else []
                d['past_participation'] = bool(d['past_participation'])
                result.append(d)
            return result
        finally:
            conn.close()

    def get_student(self, student_id: str) -> Dict[str, Any] | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['skills'] = json.loads(d['skills']) if d['skills'] else []
                d['interests'] = json.loads(d['interests']) if d['interests'] else []
                d['past_participation'] = bool(d['past_participation'])
                return d
            return None
        finally:
            conn.close()

    def get_student_by_email(self, email: str) -> Dict[str, Any] | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d['skills'] = json.loads(d['skills']) if d['skills'] else []
                d['interests'] = json.loads(d['interests']) if d['interests'] else []
                d['past_participation'] = bool(d['past_participation'])
                return d
            return None
        finally:
            conn.close()

    def add_student(self, student_data: Dict[str, Any]):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO students
                   (id, name, email, phone, age, education, college, cgpa,
                    skills, interests, location_preference, location_type,
                    category, experience, past_participation, created_at, password)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    student_data['id'], student_data.get('name'),
                    student_data.get('email'), student_data.get('phone'),
                    student_data.get('age'), student_data.get('education'),
                    student_data.get('college'), student_data.get('cgpa'),
                    json.dumps(student_data.get('skills', [])),
                    json.dumps(student_data.get('interests', [])),
                    student_data.get('location_preference'),
                    student_data.get('location_type'),
                    student_data.get('category'),
                    student_data.get('experience'),
                    1 if student_data.get('past_participation') else 0,
                    student_data.get('created_at'),
                    student_data.get('password', ''),
                )
            )
            conn.commit()
        finally:
            conn.close()

    def get_all_internships(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM internships")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d['required_skills'] = json.loads(d['required_skills']) if d['required_skills'] else []
                d['affirmative_action_required'] = bool(d['affirmative_action_required'])
                result.append(d)
            return result
        finally:
            conn.close()

    def get_all_matches(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM matches")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d['matches'] = json.loads(d['matches']) if d['matches'] else []
                result.append(d)
            return result
        finally:
            conn.close()

    def add_match(self, match_data: Dict[str, Any]):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM matches WHERE student_id = ?",
                (match_data.get('student_id'),)
            )
            cursor.execute(
                """INSERT INTO matches (student_id, matches, timestamp)
                   VALUES (?, ?, ?)""",
                (
                    match_data.get('student_id'),
                    json.dumps(match_data.get('matches', [])),
                    match_data.get('timestamp'),
                )
            )
            conn.commit()
        finally:
            conn.close()

    def get_all_admins(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_admin_by_email(self, email: str) -> Dict[str, Any] | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_admin_by_id(self, admin_id: str) -> Dict[str, Any] | None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def add_admin(self, admin_data: Dict[str, Any]):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO admins (id, name, email, password, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    admin_data['id'], admin_data.get('name'),
                    admin_data.get('email'), admin_data.get('password'),
                    admin_data.get('created_at'),
                )
            )
            conn.commit()
        finally:
            conn.close()

    def add_internship(self, internship_data: Dict[str, Any]):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO internships
                   (id, title, organization, sector, location, duration,
                    stipend, required_skills, education_requirement,
                    description, capacity, affirmative_action_required, apply_url)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    internship_data['id'], internship_data.get('title'),
                    internship_data.get('organization'), internship_data.get('sector'),
                    internship_data.get('location'), internship_data.get('duration'),
                    internship_data.get('stipend', 0),
                    json.dumps(internship_data.get('required_skills', [])),
                    internship_data.get('education_requirement', 'undergraduate'),
                    internship_data.get('description', ''),
                    internship_data.get('capacity', 0),
                    1 if internship_data.get('affirmative_action_required') else 0,
                    internship_data.get('apply_url', ''),
                )
            )
            conn.commit()
        finally:
            conn.close()

    def update_internship(self, internship_id: str, internship_data: Dict[str, Any]):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE internships
                   SET title=?, organization=?, sector=?, location=?, duration=?,
                       stipend=?, required_skills=?, education_requirement=?,
                       description=?, capacity=?, affirmative_action_required=?, apply_url=?
                   WHERE id=?""",
                (
                    internship_data.get('title'), internship_data.get('organization'),
                    internship_data.get('sector'), internship_data.get('location'),
                    internship_data.get('duration'), internship_data.get('stipend', 0),
                    json.dumps(internship_data.get('required_skills', [])),
                    internship_data.get('education_requirement', 'undergraduate'),
                    internship_data.get('description', ''),
                    internship_data.get('capacity', 0),
                    1 if internship_data.get('affirmative_action_required') else 0,
                    internship_data.get('apply_url', ''),
                    internship_id,
                )
            )
            conn.commit()
        finally:
            conn.close()

    def delete_internship(self, internship_id: str):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM internships WHERE id = ?", (internship_id,))
            conn.commit()
        finally:
            conn.close()

    def _get_sample_internships(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'INT001', 'title': 'Digital Marketing Intern',
                'organization': 'Ministry of Electronics and IT',
                'sector': 'Technology', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 15000,
                'required_skills': ['Digital Marketing', 'Social Media', 'Content Writing', 'Analytics'],
                'education_requirement': 'undergraduate',
                'description': 'Support digital initiatives and social media campaigns for government technology programs.',
                'capacity': 50, 'affirmative_action_required': True,
                'apply_url': 'https://meity.gov.in/internships'
            },
            {
                'id': 'INT002', 'title': 'Data Analytics Intern',
                'organization': 'National Sample Survey Office',
                'sector': 'Research & Analytics', 'location': 'Mumbai',
                'duration': '6 months', 'stipend': 18000,
                'required_skills': ['Python', 'Data Analysis', 'Statistics', 'Excel'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in analyzing survey data and generating insights for policy making.',
                'capacity': 30, 'affirmative_action_required': False,
                'apply_url': 'https://mospi.gov.in/internships'
            },
            {
                'id': 'INT003', 'title': 'Cybersecurity Analyst Intern',
                'organization': 'National Cyber Security Centre',
                'sector': 'Cybersecurity', 'location': 'Hyderabad',
                'duration': '6 months', 'stipend': 22000,
                'required_skills': ['Cybersecurity', 'Network Security', 'Ethical Hacking', 'Python'],
                'education_requirement': 'undergraduate',
                'description': 'Support cybersecurity initiatives and threat analysis.',
                'capacity': 20, 'affirmative_action_required': False,
                'apply_url': 'https://cert-in.org.in/internships'
            },
            {
                'id': 'INT004', 'title': 'AI Research Assistant',
                'organization': 'Centre for Development of Advanced Computing',
                'sector': 'Technology', 'location': 'Bangalore',
                'duration': '8 months', 'stipend': 25000,
                'required_skills': ['Machine Learning', 'Python', 'Research', 'Mathematics'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in artificial intelligence research projects and algorithm development.',
                'capacity': 15, 'affirmative_action_required': True,
                'apply_url': 'https://cdac.in/internships'
            },
            {
                'id': 'INT005', 'title': 'Software Development Intern',
                'organization': 'National Informatics Centre',
                'sector': 'Technology', 'location': 'Pune',
                'duration': '6 months', 'stipend': 20000,
                'required_skills': ['Java', 'JavaScript', 'Database Management', 'Web Development'],
                'education_requirement': 'undergraduate',
                'description': 'Develop government web applications and digital services.',
                'capacity': 40, 'affirmative_action_required': True,
                'apply_url': 'https://nic.gov.in/internships'
            },
            {
                'id': 'INT006', 'title': 'Healthcare Analytics Intern',
                'organization': 'All Institute of Medical Sciences',
                'sector': 'Healthcare', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 16000,
                'required_skills': ['Healthcare', 'Data Analysis', 'Medical Research', 'Statistics'],
                'education_requirement': 'undergraduate',
                'description': 'Support healthcare data analysis and medical research projects.',
                'capacity': 40, 'affirmative_action_required': True,
                'apply_url': 'https://aiims.edu/internships'
            },
            {
                'id': 'INT007', 'title': 'Public Health Research Intern',
                'organization': 'National Centre for Disease Control',
                'sector': 'Healthcare', 'location': 'Chennai',
                'duration': '8 months', 'stipend': 14000,
                'required_skills': ['Public Health', 'Epidemiology', 'Research', 'Data Collection'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in disease surveillance and public health research programs.',
                'capacity': 25, 'affirmative_action_required': True,
                'apply_url': 'https://ncdc.gov.in/internships'
            },
            {
                'id': 'INT008', 'title': 'Medical Technology Intern',
                'organization': 'Indian Council of Medical Research',
                'sector': 'Healthcare', 'location': 'Mumbai',
                'duration': '6 months', 'stipend': 18000,
                'required_skills': ['Biomedical Engineering', 'Medical Devices', 'Research', 'Technology'],
                'education_requirement': 'undergraduate',
                'description': 'Support medical technology development and innovation projects.',
                'capacity': 20, 'affirmative_action_required': False,
                'apply_url': 'https://icmr.gov.in/internships'
            },
            {
                'id': 'INT009', 'title': 'Financial Analysis Intern',
                'organization': 'Reserve Bank of India',
                'sector': 'Finance & Banking', 'location': 'Mumbai',
                'duration': '6 months', 'stipend': 20000,
                'required_skills': ['Financial Analysis', 'Economics', 'Excel', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in economic research and financial market analysis.',
                'capacity': 25, 'affirmative_action_required': False,
                'apply_url': 'https://rbi.org.in/internships'
            },
            {
                'id': 'INT010', 'title': 'Banking Operations Intern',
                'organization': 'State Bank of India',
                'sector': 'Finance & Banking', 'location': 'Kolkata',
                'duration': '4 months', 'stipend': 12000,
                'required_skills': ['Banking Operations', 'Customer Service', 'Documentation', 'Finance'],
                'education_requirement': 'undergraduate',
                'description': 'Learn banking operations and customer service in public sector banking.',
                'capacity': 60, 'affirmative_action_required': True,
                'apply_url': 'https://sbi.co.in/internships'
            },
            {
                'id': 'INT011', 'title': 'Investment Research Intern',
                'organization': 'Securities and Exchange Board of India',
                'sector': 'Finance & Banking', 'location': 'Mumbai',
                'duration': '6 months', 'stipend': 22000,
                'required_skills': ['Investment Analysis', 'Capital Markets', 'Research', 'Excel'],
                'education_requirement': 'undergraduate',
                'description': 'Research market trends and support investment regulation activities.',
                'capacity': 15, 'affirmative_action_required': False,
                'apply_url': 'https://sebi.gov.in/internships'
            },
            {
                'id': 'INT012', 'title': 'Education Technology Intern',
                'organization': 'Ministry of Education',
                'sector': 'Education', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 15000,
                'required_skills': ['Education Technology', 'Content Development', 'Learning Design', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Develop educational content and support digital learning initiatives.',
                'capacity': 45, 'affirmative_action_required': True,
                'apply_url': 'https://education.gov.in/internships'
            },
            {
                'id': 'INT013', 'title': 'Research Assistant - Higher Education',
                'organization': 'University Grants Commission',
                'sector': 'Education', 'location': 'Bangalore',
                'duration': '8 months', 'stipend': 16000,
                'required_skills': ['Research', 'Academic Writing', 'Data Analysis', 'Higher Education'],
                'education_requirement': 'undergraduate',
                'description': 'Support research in higher education policy and development.',
                'capacity': 30, 'affirmative_action_required': True,
                'apply_url': 'https://ugc.ac.in/internships'
            },
            {
                'id': 'INT014', 'title': 'Skill Development Program Intern',
                'organization': 'Ministry of Skill Development',
                'sector': 'Education', 'location': 'Bhopal',
                'duration': '6 months', 'stipend': 13000,
                'required_skills': ['Training Design', 'Program Management', 'Documentation', 'Communication'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in designing and implementing skill development programs.',
                'capacity': 50, 'affirmative_action_required': True,
                'apply_url': 'https://msde.gov.in/internships'
            },
            {
                'id': 'INT015', 'title': 'Rural Development Assistant',
                'organization': 'Ministry of Rural Development',
                'sector': 'Rural Development', 'location': 'Bhopal',
                'duration': '8 months', 'stipend': 12000,
                'required_skills': ['Project Management', 'Community Engagement', 'Documentation'],
                'education_requirement': 'undergraduate',
                'description': 'Support rural development programs and community outreach initiatives.',
                'capacity': 75, 'affirmative_action_required': True,
                'apply_url': 'https://rd.gov.in/internships'
            },
            {
                'id': 'INT016', 'title': 'Agricultural Research Intern',
                'organization': 'Indian Agricultural Research Institute',
                'sector': 'Agriculture', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 14000,
                'required_skills': ['Agriculture', 'Research', 'Data Collection', 'Laboratory Skills'],
                'education_requirement': 'undergraduate',
                'description': 'Support agricultural research and crop development studies.',
                'capacity': 35, 'affirmative_action_required': True,
                'apply_url': 'https://iari.res.in/internships'
            },
            {
                'id': 'INT017', 'title': 'Farm Technology Intern',
                'organization': 'Central Institute of Agricultural Engineering',
                'sector': 'Agriculture', 'location': 'Chandigarh',
                'duration': '6 months', 'stipend': 15000,
                'required_skills': ['Agricultural Technology', 'Engineering', 'Innovation', 'Field Work'],
                'education_requirement': 'undergraduate',
                'description': 'Work on farm mechanization and agricultural technology projects.',
                'capacity': 25, 'affirmative_action_required': True,
                'apply_url': 'https://ciae.gov.in/internships'
            },
            {
                'id': 'INT018', 'title': 'Environmental Policy Intern',
                'organization': 'Ministry of Environment and Forests',
                'sector': 'Environment', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 14000,
                'required_skills': ['Environmental Science', 'Policy Research', 'Documentation', 'GIS'],
                'education_requirement': 'undergraduate',
                'description': 'Research and develop environmental policies and sustainability initiatives.',
                'capacity': 35, 'affirmative_action_required': True,
                'apply_url': 'https://moef.gov.in/internships'
            },
            {
                'id': 'INT019', 'title': 'Climate Change Research Intern',
                'organization': 'National Environmental Engineering Research Institute',
                'sector': 'Environment', 'location': 'Pune',
                'duration': '8 months', 'stipend': 16000,
                'required_skills': ['Climate Science', 'Research', 'Data Analysis', 'Environmental Monitoring'],
                'education_requirement': 'undergraduate',
                'description': 'Study climate change impacts and adaptation strategies.',
                'capacity': 20, 'affirmative_action_required': True,
                'apply_url': 'https://neeri.res.in/internships'
            },
            {
                'id': 'INT020', 'title': 'Wildlife Conservation Intern',
                'organization': 'Wildlife Institute of India',
                'sector': 'Environment', 'location': 'Dehradun',
                'duration': '6 months', 'stipend': 13000,
                'required_skills': ['Wildlife Biology', 'Conservation', 'Field Research', 'Photography'],
                'education_requirement': 'undergraduate',
                'description': 'Support wildlife conservation research and habitat protection programs.',
                'capacity': 30, 'affirmative_action_required': True,
                'apply_url': 'https://wiigoa.gov.in/internships'
            },
            {
                'id': 'INT021', 'title': 'Defence Research Intern',
                'organization': 'Defence Research and Development Organisation',
                'sector': 'Defence', 'location': 'Bangalore',
                'duration': '6 months', 'stipend': 20000,
                'required_skills': ['Engineering', 'Research', 'Technology', 'Innovation'],
                'education_requirement': 'undergraduate',
                'description': 'Assist in defence technology research and development projects.',
                'capacity': 25, 'affirmative_action_required': False,
                'apply_url': 'https://drdo.gov.in/internships'
            },
            {
                'id': 'INT022', 'title': 'Border Security Technology Intern',
                'organization': 'Border Security Force',
                'sector': 'Defence', 'location': 'New Delhi',
                'duration': '4 months', 'stipend': 18000,
                'required_skills': ['Security Technology', 'Surveillance', 'Electronics', 'Communication'],
                'education_requirement': 'undergraduate',
                'description': 'Work on border security technology and surveillance systems.',
                'capacity': 20, 'affirmative_action_required': True,
                'apply_url': 'https://bsf.gov.in/internships'
            },
            {
                'id': 'INT023', 'title': 'Satellite Technology Intern',
                'organization': 'Indian Space Research Organisation',
                'sector': 'Space & Aerospace', 'location': 'Bangalore',
                'duration': '8 months', 'stipend': 25000,
                'required_skills': ['Aerospace Engineering', 'Satellite Technology', 'Programming', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Support satellite development and space technology projects.',
                'capacity': 15, 'affirmative_action_required': False,
                'apply_url': 'https://isro.gov.in/internships'
            },
            {
                'id': 'INT024', 'title': 'Space Applications Intern',
                'organization': 'National Remote Sensing Centre',
                'sector': 'Space & Aerospace', 'location': 'Hyderabad',
                'duration': '6 months', 'stipend': 20000,
                'required_skills': ['Remote Sensing', 'GIS', 'Data Analysis', 'Programming'],
                'education_requirement': 'undergraduate',
                'description': 'Work on satellite data applications for earth observation.',
                'capacity': 25, 'affirmative_action_required': True,
                'apply_url': 'https://nrsa.gov.in/internships'
            },
            {
                'id': 'INT025', 'title': 'Railway Engineering Intern',
                'organization': 'Indian Railways',
                'sector': 'Transportation', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 16000,
                'required_skills': ['Mechanical Engineering', 'Railway Systems', 'Maintenance', 'Safety'],
                'education_requirement': 'undergraduate',
                'description': 'Support railway engineering and infrastructure development.',
                'capacity': 50, 'affirmative_action_required': True,
                'apply_url': 'https://indianrailways.gov.in/internships'
            },
            {
                'id': 'INT026', 'title': 'Smart Transportation Intern',
                'organization': 'Ministry of Road Transport and Highways',
                'sector': 'Transportation', 'location': 'Mumbai',
                'duration': '6 months', 'stipend': 18000,
                'required_skills': ['Transportation Planning', 'Smart Systems', 'Data Analysis', 'Urban Planning'],
                'education_requirement': 'undergraduate',
                'description': 'Work on smart transportation systems and traffic management.',
                'capacity': 30, 'affirmative_action_required': False,
                'apply_url': 'https://morth.nic.in/internships'
            },
            {
                'id': 'INT027', 'title': 'Cultural Heritage Preservation Intern',
                'organization': 'Archaeological Survey of India',
                'sector': 'Tourism & Culture', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 12000,
                'required_skills': ['Archaeology', 'History', 'Documentation', 'Research'],
                'education_requirement': 'undergraduate',
                'description': 'Support cultural heritage preservation and archaeological projects.',
                'capacity': 40, 'affirmative_action_required': True,
                'apply_url': 'https://asi.nic.in/internships'
            },
            {
                'id': 'INT028', 'title': 'Digital Tourism Promotion Intern',
                'organization': 'Ministry of Tourism',
                'sector': 'Tourism & Culture', 'location': 'Goa',
                'duration': '4 months', 'stipend': 15000,
                'required_skills': ['Digital Marketing', 'Tourism', 'Content Creation', 'Social Media'],
                'education_requirement': 'undergraduate',
                'description': 'Promote Indian tourism through digital marketing initiatives.',
                'capacity': 35, 'affirmative_action_required': True,
                'apply_url': 'https://tourism.gov.in/internships'
            },
            {
                'id': 'INT029', 'title': 'Renewable Energy Research Intern',
                'organization': 'Solar Energy Corporation of India',
                'sector': 'Energy', 'location': 'Gurugram',
                'duration': '6 months', 'stipend': 18000,
                'required_skills': ['Renewable Energy', 'Solar Technology', 'Research', 'Engineering'],
                'education_requirement': 'undergraduate',
                'description': 'Research renewable energy technologies and solar power systems.',
                'capacity': 30, 'affirmative_action_required': True,
                'apply_url': 'https://seci.co.in/internships'
            },
            {
                'id': 'INT030', 'title': 'Power Grid Analytics Intern',
                'organization': 'Power Grid Corporation of India',
                'sector': 'Energy', 'location': 'New Delhi',
                'duration': '6 months', 'stipend': 20000,
                'required_skills': ['Power Systems', 'Data Analysis', 'Engineering', 'Grid Management'],
                'education_requirement': 'undergraduate',
                'description': 'Analyze power grid performance and optimization strategies.',
                'capacity': 25, 'affirmative_action_required': False,
                'apply_url': 'https://powergrid.in/internships'
            },
        ]
