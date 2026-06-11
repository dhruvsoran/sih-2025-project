from flask import render_template, request, session, redirect, url_for, jsonify, flash, make_response
from app import app
from data_manager import DataManager
from matching_engine import MatchingEngine
from internship_fetcher import InternshipFetcher
from email_utils import generate_verification_token, send_verification_email, BASE_URL
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
import tempfile
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

data_manager = DataManager()
matching_engine = MatchingEngine()

@app.after_request
def add_security_headers(response):
    """Add security headers to every response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'"
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/robots.txt')
def robots_txt():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    response = make_response(open(os.path.join(base_dir, 'static', 'robots.txt')).read())
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/sitemap.xml')
def sitemap_xml():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    response = make_response(open(os.path.join(base_dir, 'static', 'sitemap.xml')).read())
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Prayaas'}), 200

@app.before_request
def validate_session():
    """Validate session on every request - clear stale sessions"""
    if session.get('student_id'):
        student = data_manager.get_student(session['student_id'])
        if not student:
            session.clear()
    if session.get('admin_id') and session.get('is_admin'):
        admin = data_manager.get_admin_by_id(session['admin_id'])
        if not admin:
            session.clear()

def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id') or not session.get('is_admin'):
            flash('Access denied. Please log in as admin.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to require student authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('student_id'):
            flash('Please login or register to continue.', 'error')
            return redirect(url_for('student_login'))
        student = data_manager.get_student(session['student_id'])
        if not student:
            session.clear()
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    students = data_manager.get_all_students()
    internships = data_manager.get_all_internships()
    matches = data_manager.get_all_matches()
    
    stats = {
        'total_students': len(students),
        'total_internships': len(internships),
        'total_matches': len(matches),
        'match_rate': (len(matches) / len(students) * 100) if len(students) > 0 else 0
    }
    
    return render_template('index.html', stats=stats)

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        if session.get('student_id'):
            return redirect(url_for('student_dashboard'))
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Email and password are required.', 'error')
        else:
            # Check admin first
            admin = data_manager.get_admin_by_email(email)
            if admin and check_password_hash(admin['password'], password):
                session['admin_id'] = admin['id']
                session['is_admin'] = True
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            # Check student
            student = data_manager.get_student_by_email(email)
            if student and student.get('password') and check_password_hash(student['password'], password):
                if not student.get('email_verified'):
                    # Store student_id in session so resend-verification knows who they are
                    session['pending_verify_id'] = student['id']
                    session['pending_verify_email'] = student['email']
                    flash('Please verify your email before logging in. Check your inbox or resend the verification email.', 'error')
                    return redirect(url_for('resend_verification'))
                session['student_id'] = student['id']
                flash(f'Welcome back, {student["name"]}!', 'success')
                return redirect(url_for('student_dashboard'))
            elif student and not student.get('password'):
                flash('This account was created via registration. Please use "Register" to set a password.', 'error')
            else:
                flash('Invalid email or password.', 'error')
    return render_template('student_login.html')

@app.route('/student')
@student_required
def student_dashboard():
    student_id = session.get('student_id')
    student = data_manager.get_student(student_id)
    return render_template('student_dashboard.html', student=student)

@app.route('/admin')
@admin_required
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
        password = request.form.get('password', '')
        verification_token = generate_verification_token()
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
            'created_at': datetime.now().isoformat(),
            'password': generate_password_hash(password) if password else '',
            'email_verified': False,
            'verification_token': verification_token,
        }
        
        # Save student data
        data_manager.add_student(student_data)
        
        # Send verification email
        send_verification_email(
            student_data['email'],
            student_data['name'],
            verification_token
        )
        
        # Set session so the verify page knows who just registered
        session['student_id'] = student_id
        session['pending_verify_email'] = student_data['email']
        
        flash('Account created! Please check your email and verify your account.', 'success')
        return redirect(url_for('resend_verification'))
    
    return render_template('profile_form.html')

@app.route('/match/<student_id>')
@student_required
def run_matching(student_id):
    # Verify the student owns this profile
    if session.get('student_id') != student_id:
        flash('Access denied. You can only access your own profile.', 'error')
        return redirect(url_for('student_dashboard'))
    
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

@app.route('/live-match/<student_id>')
@student_required
def live_match(student_id):
    """Fetch live internships from Indeed/LinkedIn/Naukri and match against student profile."""
    if session.get('student_id') != student_id:
        flash('Access denied.', 'error')
        return redirect(url_for('student_dashboard'))
    
    student = data_manager.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student_dashboard'))
    
    location = request.args.get('location', student.get('location_preference', ''))
    search_query = request.args.get('query', '')
    
    # Fetch live internships from external platforms
    fetcher = InternshipFetcher()
    live_internships = fetcher.fetch_all(
        query=search_query,
        location=location,
        skills=student.get('skills', []),
        max_per_platform=12
    )
    
    live_matches = matching_engine.find_live_matches(student, live_internships)
    
    # Also include internal database matches
    internal_internships = data_manager.get_all_internships()
    internal_matches = matching_engine.find_matches(student, internal_internships)
    
    # Convert internal matches to same format as live matches
    for m in internal_matches:
        m['internship']['platform'] = 'Prayaas Database'
        m['source'] = 'internal'
    
    for m in live_matches:
        m['source'] = 'live'
    
    # Combine: internal first, then live
    all_matches = internal_matches + live_matches
    
    platforms_found = list(set(m['internship'].get('platform', '') for m in all_matches))
    
    return render_template('live_matching_results.html',
                         student=student,
                         matches=all_matches,
                         search_query=search_query,
                         location=location,
                         platforms_found=platforms_found,
                         total_fetched=len(live_internships) + len(internal_internships))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.info(f"Admin login attempt: email={email}")
        
        if not email or not password:
            flash('Email and password are required.', 'error')
        else:
            admin = data_manager.get_admin_by_email(email)
            logger.info(f"Admin found: {admin is not None}")
            if admin:
                pwd_ok = check_password_hash(admin['password'], password)
                logger.info(f"Password valid: {pwd_ok}")
                if pwd_ok:
                    session['admin_id'] = admin['id']
                    session['is_admin'] = True
                    flash('Successfully logged in as admin!', 'success')
                    return redirect(url_for('admin_dashboard'))
            flash('Invalid email or password.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/signup')
def admin_signup():
    flash('Admin registration is not available. Please contact the system administrator.', 'error')
    return redirect(url_for('admin_login'))

@app.route('/api/match-all')
@admin_required
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

@app.route('/admin/internships', methods=['GET', 'POST'])
@admin_required
def admin_internships():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            internship_data = {
                'id': 'INT' + str(int(datetime.now().timestamp())),
                'title': request.form.get('title'),
                'organization': request.form.get('organization'),
                'sector': request.form.get('sector'),
                'location': request.form.get('location'),
                'duration': request.form.get('duration'),
                'stipend': int(request.form.get('stipend', 0)),
                'required_skills': [s.strip() for s in request.form.get('required_skills', '').split(',') if s.strip()],
                'education_requirement': request.form.get('education_requirement', 'undergraduate'),
                'description': request.form.get('description', ''),
                'capacity': int(request.form.get('capacity', 0)),
                'affirmative_action_required': request.form.get('affirmative_action_required') == 'on',
                'apply_url': request.form.get('apply_url', '')
            }
            data_manager.add_internship(internship_data)
            flash('Internship added successfully!', 'success')
            return redirect(url_for('admin_internships'))
        
        elif action == 'edit':
            internship_id = request.form.get('internship_id')
            internship_data = {
                'title': request.form.get('title'),
                'organization': request.form.get('organization'),
                'sector': request.form.get('sector'),
                'location': request.form.get('location'),
                'duration': request.form.get('duration'),
                'stipend': int(request.form.get('stipend', 0)),
                'required_skills': [s.strip() for s in request.form.get('required_skills', '').split(',') if s.strip()],
                'education_requirement': request.form.get('education_requirement', 'undergraduate'),
                'description': request.form.get('description', ''),
                'capacity': int(request.form.get('capacity', 0)),
                'affirmative_action_required': request.form.get('affirmative_action_required') == 'on',
                'apply_url': request.form.get('apply_url', '')
            }
            data_manager.update_internship(internship_id, internship_data)
            flash('Internship updated successfully!', 'success')
            return redirect(url_for('admin_internships'))
        
        elif action == 'delete':
            internship_id = request.form.get('internship_id')
            data_manager.delete_internship(internship_id)
            flash('Internship deleted successfully!', 'success')
            return redirect(url_for('admin_internships'))
    
    internships = data_manager.get_all_internships()
    return render_template('admin_internships.html', internships=internships)

@app.route('/admin/students/delete', methods=['POST'])
@admin_required
def admin_delete_student():
    """Delete a student from the database."""
    student_id = request.form.get('student_id')
    if student_id:
        student = data_manager.get_student(student_id)
        if student:
            data_manager.delete_student(student_id)
            flash(f'Student "{student["name"]}" deleted successfully.', 'success')
        else:
            flash('Student not found.', 'error')
    else:
        flash('No student ID provided.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logs')
@admin_required
def admin_logs():
    """View activity logs for the admin panel."""
    students = data_manager.get_all_students()
    matches = data_manager.get_all_matches()
    internships = data_manager.get_all_internships()

    logs = []
    for s in students:
        logs.append({
            'type': 'registration',
            'icon': 'fas fa-user-plus',
            'color': 'var(--blue)',
            'message': f'{s["name"]} registered',
            'detail': s.get('email', ''),
            'timestamp': s.get('created_at', ''),
        })
    for m in matches:
        student = next((s for s in students if s['id'] == m['student_id']), None)
        name = student['name'] if student else 'Unknown'
        top_match = m['matches'][0]['internship']['title'] if m.get('matches') else 'No matches'
        score = m['matches'][0]['score'] if m.get('matches') else 0
        logs.append({
            'type': 'match',
            'icon': 'fas fa-handshake',
            'color': 'var(--green)',
            'message': f'{name} matched with {top_match}',
            'detail': f'Score: {score}%',
            'timestamp': m.get('timestamp', ''),
        })

    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return render_template('admin_logs.html',
                         logs=logs,
                         stats={
                             'total_students': len(students),
                             'total_matches': len(matches),
                             'total_internships': len(internships),
                         })

@app.route('/upload-resume', methods=['GET', 'POST'])
@student_required
def upload_resume():
    """Upload resume and get AI-powered internship recommendations."""
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected. Please choose a resume to upload.', 'error')
            return redirect(url_for('upload_resume'))
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected. Please choose a resume to upload.', 'error')
            return redirect(url_for('upload_resume'))
        
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            flash('Unsupported file format. Please upload a PDF or DOCX file.', 'error')
            return redirect(url_for('upload_resume'))
        
        # Validate file size (max 5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 5 * 1024 * 1024:
            flash('File too large. Please upload a resume under 5MB.', 'error')
            return redirect(url_for('upload_resume'))
        
        # Save file temporarily
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name
            
            # Parse resume
            from resume_parser import parse_resume
            resume_data = parse_resume(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            if 'error' in resume_data:
                flash(f'Error parsing resume: {resume_data["error"]}', 'error')
                return redirect(url_for('upload_resume'))
            
            # Get student's current profile data
            student_id = session.get('student_id')
            student = data_manager.get_student(student_id)
            
            # Merge resume data with student profile for matching
            # Use resume skills if available, otherwise use profile skills
            matching_skills = resume_data.get('skills', []) or student.get('skills', [])
            matching_interests = resume_data.get('interests', []) or student.get('interests', [])
            
            # Create a virtual student profile for matching
            virtual_student = {
                'id': student_id,
                'name': resume_data.get('name', student.get('name', '')),
                'skills': matching_skills,
                'interests': matching_interests,
                'education': resume_data.get('education', student.get('education', 'undergraduate')),
                'cgpa': student.get('cgpa', 7.0),
                'location_preference': student.get('location_preference', 'any'),
                'location_type': student.get('location_type', 'urban'),
                'category': student.get('category', 'General'),
                'past_participation': student.get('past_participation', False),
                'experience': resume_data.get('experience', student.get('experience', 'fresher')),
            }
            
            # Run matching against internal internships
            internships = data_manager.get_all_internships()
            internal_matches = matching_engine.find_matches(virtual_student, internships)
            
            # Run live matching
            from internship_fetcher import InternshipFetcher
            fetcher = InternshipFetcher()
            live_internships = fetcher.fetch_all(
                query='',
                location=student.get('location_preference', ''),
                skills=matching_skills,
                max_per_platform=8
            )
            live_matches = matching_engine.find_live_matches(virtual_student, live_internships)
            
            return render_template('resume_results.html',
                                 resume_data=resume_data,
                                 student=student,
                                 internal_matches=internal_matches,
                                 live_matches=live_matches)
        
        except Exception as e:
            flash(f'Error processing resume: {str(e)}', 'error')
            return redirect(url_for('upload_resume'))
    
    student = data_manager.get_student(session.get('student_id'))
    return render_template('upload_resume.html', student=student)

@app.route('/verify/<token>')
def verify_email(token):
    """Verify a student's email address via the token sent to their inbox."""
    if data_manager.verify_student_email(token):
        flash('Email verified successfully! You can now log in.', 'success')
        # Clear any pending verification session data
        session.pop('pending_verify_id', None)
        session.pop('pending_verify_email', None)
        return redirect(url_for('student_login'))
    else:
        flash('Invalid or expired verification link. Please resend the verification email.', 'error')
        return redirect(url_for('resend_verification'))


@app.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email or show the pending verification page."""
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('resend_verification'))

        student = data_manager.get_student_by_email(email)
        if not student:
            flash('No account found with that email.', 'error')
            return redirect(url_for('resend_verification'))

        if student.get('email_verified'):
            flash('Your email is already verified. You can log in.', 'success')
            return redirect(url_for('student_login'))

        # Generate new token and send
        token = generate_verification_token()
        data_manager.update_verification_token(student['id'], token)
        send_verification_email(student['email'], student['name'], token)

        session['pending_verify_id'] = student['id']
        session['pending_verify_email'] = student['email']

        flash('Verification email resent! Check your inbox.', 'success')
        return redirect(url_for('resend_verification'))

    # GET - show the pending verification page
    pending_email = session.get('pending_verify_email', '')
    return render_template('verify_pending.html', email=pending_email)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))
