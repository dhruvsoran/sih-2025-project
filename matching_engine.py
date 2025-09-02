import math
from typing import List, Dict, Any

class MatchingEngine:
    """AI-powered matching engine for PM Internship Scheme"""
    
    def __init__(self):
        # Weights for different matching criteria
        self.weights = {
            'skills_match': 0.30,
            'education_match': 0.20,
            'location_preference': 0.15,
            'interest_alignment': 0.15,
            'cgpa_score': 0.10,
            'affirmative_action': 0.05,
            'past_participation': 0.05
        }
    
    def find_matches(self, student: Dict[str, Any], internships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find and rank internship matches for a student"""
        matches = []
        
        for internship in internships:
            score = self.calculate_match_score(student, internship)
            
            match = {
                'internship': internship,
                'score': round(score, 2),
                'rank': None,  # Will be set after sorting
                'reasoning': self.generate_reasoning(student, internship, score)
            }
            matches.append(match)
        
        # Sort by score and assign ranks
        matches.sort(key=lambda x: x['score'], reverse=True)
        for i, match in enumerate(matches):
            match['rank'] = i + 1
        
        return matches[:10]  # Return top 10 matches
    
    def calculate_match_score(self, student: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate matching score between student and internship"""
        
        # Skills matching
        skills_score = self.calculate_skills_match(student.get('skills', []), 
                                                 internship.get('required_skills', []))
        
        # Education level matching
        education_score = self.calculate_education_match(student.get('education', ''), 
                                                       internship.get('education_requirement', ''))
        
        # Location preference
        location_score = self.calculate_location_match(student.get('location_preference', ''), 
                                                     internship.get('location', ''))
        
        # Interest alignment
        interest_score = self.calculate_interest_match(student.get('interests', []), 
                                                     internship.get('sector', ''))
        
        # CGPA score (normalized)
        cgpa_score = min(student.get('cgpa', 0) / 10.0, 1.0)
        
        # Affirmative action bonus
        affirmative_score = self.calculate_affirmative_action_bonus(student, internship)
        
        # Past participation penalty/bonus
        participation_score = self.calculate_participation_score(student)
        
        # Calculate weighted score
        total_score = (
            skills_score * self.weights['skills_match'] +
            education_score * self.weights['education_match'] +
            location_score * self.weights['location_preference'] +
            interest_score * self.weights['interest_alignment'] +
            cgpa_score * self.weights['cgpa_score'] +
            affirmative_score * self.weights['affirmative_action'] +
            participation_score * self.weights['past_participation']
        ) * 100
        
        return max(0, min(100, total_score))
    
    def calculate_skills_match(self, student_skills: List[str], required_skills: List[str]) -> float:
        """Calculate skills matching score"""
        if not required_skills:
            return 0.5
        
        matched_skills = set(student_skills).intersection(set(required_skills))
        return len(matched_skills) / len(required_skills)
    
    def calculate_education_match(self, student_education: str, required_education: str) -> float:
        """Calculate education level matching"""
        education_hierarchy = {
            'high school': 1,
            '12th': 2,
            'diploma': 3,
            'undergraduate': 4,
            'bachelor': 4,
            'postgraduate': 5,
            'master': 5,
            'phd': 6
        }
        
        student_level = education_hierarchy.get(student_education.lower(), 0)
        required_level = education_hierarchy.get(required_education.lower(), 0)
        
        if student_level >= required_level:
            return 1.0
        else:
            return student_level / required_level if required_level > 0 else 0.5
    
    def calculate_location_match(self, student_preference: str, internship_location: str) -> float:
        """Calculate location preference matching"""
        if student_preference.lower() == 'any' or not student_preference:
            return 0.7
        
        if student_preference.lower() in internship_location.lower():
            return 1.0
        else:
            return 0.3
    
    def calculate_interest_match(self, student_interests: List[str], internship_sector: str) -> float:
        """Calculate interest alignment score"""
        if not student_interests:
            return 0.5
        
        for interest in student_interests:
            if interest.lower() in internship_sector.lower():
                return 1.0
        
        return 0.3
    
    def calculate_affirmative_action_bonus(self, student: Dict[str, Any], internship: Dict[str, Any]) -> float:
        """Calculate affirmative action compliance bonus"""
        bonus = 0.0
        
        # Rural/aspirational district bonus
        if student.get('location_type') == 'rural':
            bonus += 0.3
        
        # Social category bonus
        if student.get('category') in ['SC', 'ST']:
            bonus += 0.4
        elif student.get('category') == 'OBC':
            bonus += 0.2
        
        # Check if internship has affirmative action requirements
        if internship.get('affirmative_action_required', False):
            bonus += 0.3
        
        return min(bonus, 1.0)
    
    def calculate_participation_score(self, student: Dict[str, Any]) -> float:
        """Calculate score based on past participation"""
        if student.get('past_participation', False):
            return 0.3  # Slight penalty for repeat participation
        else:
            return 1.0  # Bonus for new participants
    
    def generate_reasoning(self, student: Dict[str, Any], internship: Dict[str, Any], score: float) -> List[str]:
        """Generate human-readable reasoning for the match"""
        reasons = []
        
        # Skills analysis
        student_skills = set(student.get('skills', []))
        required_skills = set(internship.get('required_skills', []))
        matched_skills = student_skills.intersection(required_skills)
        
        if matched_skills:
            reasons.append(f"Skills match: {', '.join(matched_skills)}")
        
        if len(matched_skills) < len(required_skills):
            missing_skills = required_skills - student_skills
            reasons.append(f"Missing skills: {', '.join(missing_skills)}")
        
        # Education match
        if student.get('education', '').lower() in ['bachelor', 'undergraduate', 'postgraduate', 'master']:
            reasons.append("Education requirement satisfied")
        
        # Location preference
        if student.get('location_preference', '').lower() in internship.get('location', '').lower():
            reasons.append("Location preference matches")
        
        # CGPA consideration
        cgpa = student.get('cgpa', 0)
        if cgpa >= 8.0:
            reasons.append("Excellent academic performance")
        elif cgpa >= 7.0:
            reasons.append("Good academic performance")
        
        # Affirmative action
        if student.get('location_type') == 'rural':
            reasons.append("Rural background advantage")
        
        if student.get('category') in ['SC', 'ST', 'OBC']:
            reasons.append("Social category consideration")
        
        return reasons[:5]  # Limit to top 5 reasons
