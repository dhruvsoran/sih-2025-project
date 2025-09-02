from flask import render_template, request, session, redirect, url_for, jsonify, flash
from app import app
from data_manager import DataManager
from matching_engine import MatchingEngine
import uuid
from datetime import datetime

data_manager = DataManager()
matching_engine = MatchingEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student')
def student_dashboard():
    student_id = session.get('student_id')
    student = None
    if student_id:
        student = data_manager.get_student(student_id)
    return render_template('student_dashboard.html', student=student)

@app.route('/admin')
def admin_dashboard():
    students = data_manager.get_all_students()
    internships = data_manager.get_all_internships()
    matches = data_manager.get_all_matches()
    
    # Calculate statistics
    total_students = len(students)
    total_internships = len(internships)
    total_matches = len(matches)
    
    # Calculate affirmative action stats
    rural_students = len([s for s in students if s.get('location_type') == 'rural'])
    sc_st_students = len([s for s in students if s.get('category') in ['SC', 'ST']])
    
    stats = {
        'total_students': total_students,
        'total_internships': total_internships,
        'total_matches': total_matches,
        'rural_students': rural_students,
        'sc_st_students': sc_st_students,
        'match_rate': (total_matches / total_students * 100) if total_students > 0 else 0
    }
    
    return render_template('admin_dashboard.html', 
                         students=students, 
                         internships=internships, 
                         matches=matches,
                         stats=stats)

@app.route('/profile', methods=['GET', 'POST'])
def profile_form():
    if request.method == 'POST':
        # Generate unique student ID
        student_id = str(uuid.uuid4())
        
        # Collect form data
        student_data = {
            'id': student_id,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'age': int(request.form.get('age', 0)),
            'education': request.form.get('education'),
            'college': request.form.get('college'),
            'cgpa': float(request.form.get('cgpa', 0)),
            'skills': request.form.getlist('skills'),
            'interests': request.form.getlist('interests'),
            'location_preference': request.form.get('location_preference'),
            'location_type': request.form.get('location_type'),
            'category': request.form.get('category'),
            'experience': request.form.get('experience'),
            'past_participation': request.form.get('past_participation') == 'yes',
            'created_at': datetime.now().isoformat()
        }
        
        # Save student data
        data_manager.add_student(student_data)
        session['student_id'] = student_id
        
        flash('Profile created successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('profile_form.html')

@app.route('/match/<student_id>')
def run_matching(student_id):
    student = data_manager.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Run matching algorithm
    matches = matching_engine.find_matches(student, data_manager.get_all_internships())
    
    # Save match results
    match_data = {
        'student_id': student_id,
        'matches': matches,
        'timestamp': datetime.now().isoformat()
    }
    data_manager.add_match(match_data)
    
    return render_template('matching_results.html', 
                         student=student, 
                         matches=matches)

@app.route('/api/match-all')
def match_all_students():
    """API endpoint to run matching for all students"""
    students = data_manager.get_all_students()
    internships = data_manager.get_all_internships()
    
    all_matches = []
    for student in students:
        matches = matching_engine.find_matches(student, internships)
        match_data = {
            'student_id': student['id'],
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }
        data_manager.add_match(match_data)
        all_matches.append(match_data)
    
    return jsonify({'success': True, 'total_matches': len(all_matches)})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
