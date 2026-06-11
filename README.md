# Prayaas - PM Internship Matching System

An AI-powered web application for India's **PM Internship Scheme** that intelligently matches students with government internship opportunities based on skills, education, location preferences, and affirmative action compliance.

## Features

### For Students
- **Profile Registration** - Create a detailed profile with skills, education, interests, and location preferences
- **Smart Login** - Secure email/password authentication
- **AI Matching** - Get ranked internship matches with compatibility scores (0-100%)
- **Skill Analysis** - See matched and missing skills for each internship
- **Apply Now** - Direct links to official internship application portals
- **Print Results** - Print-friendly matching results

### For Admins
- **Dashboard Analytics** - Total students, internships, matches, match rates
- **Internship Management** - Full CRUD for internships (add, edit, delete)
- **Affirmative Action Tracking** - Rural student count, SC/ST metrics
- **Batch Matching** - Run matching algorithm for all students at once
- **System Impact Metrics** - Geographic reach, skills demand, regional distribution

### Matching Algorithm
Multi-criteria weighted scoring system:
| Criteria | Weight |
|----------|--------|
| Skills Match | 30% |
| Education Compatibility | 20% |
| Location Preference | 15% |
| Interest Alignment | 15% |
| CGPA Score | 10% |
| Affirmative Action | 5% |
| Past Participation | 5% |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python) |
| Database | SQLite3 |
| Frontend | Bootstrap 5.3, Font Awesome 6.4 |
| Auth | Werkzeug (password hashing) |
| Sessions | Flask-Session (filesystem) |
| Deployment | Gunicorn |

## Project Structure

```
├── app.py                  # Flask app factory & session config
├── main.py                 # WSGI entry point
├── run.py                  # Development server runner
├── routes.py               # All route handlers
├── matching_engine.py      # AI matching algorithm
├── data_manager.py         # SQLite data access layer
├── db_config.py            # Database schema & migrations
├── requirements.txt        # Python dependencies
├── data/                   # Seed data & database
│   ├── internships.json    # 30 sample government internships
│   └── internship.db       # SQLite database (auto-created)
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with navbar
│   ├── index.html          # Landing page
│   ├── profile_form.html   # Student registration
│   ├── student_login.html  # Student login
│   ├── student_dashboard.html
│   ├── matching_results.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── admin_internships.html
└── static/
    ├── css/
    │   ├── style.css       # Core styles
    │   └── premium.css     # Premium dark theme
    └── js/
        ├── main.js         # Core JavaScript
        └── premium.js      # Premium animations
```

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd sih-2025-project

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Development Mode
```bash
python run.py
```
Opens at `http://localhost:5000`

### Production Mode
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## Default Credentials

### Admin Account (auto-seeded)
- **Email:** `admin@gmail.com`
- **Password:** `199999`

### Student Account
Register a new student profile at `/profile` or login at `/student/login`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SESSION_SECRET` | Flask session secret key | Dev fallback key |
| `SQLITE_DB_PATH` | Path to SQLite database | `data/internship.db` |

## Seed Data

The application auto-seeds **30 government internships** across 14 sectors:
- Technology, Healthcare, Finance & Banking, Education
- Agriculture, Environment, Defence, Space & Aerospace
- Transportation, Energy, Cybersecurity, Tourism & Culture
- Rural Development, Research & Analytics

Stipend range: Rs 12,000 - Rs 25,000/month

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Landing page |
| `/profile` | GET/POST | No | Student registration |
| `/student/login` | GET/POST | No | Student login |
| `/student` | GET | Student | Student dashboard |
| `/match/<student_id>` | GET | Student | Run matching |
| `/admin/login` | GET/POST | No | Admin login |
| `/admin` | GET | Admin | Admin dashboard |
| `/admin/internships` | GET/POST | Admin | Manage internships |
| `/api/match-all` | GET | Admin | Batch matching |
| `/logout` | GET | No | Clear session |

## Database Schema

### Students
| Field | Type | Description |
|-------|------|-------------|
| id | TEXT (PK) | UUID |
| name | TEXT | Full name |
| email | TEXT | Email address |
| password | TEXT | Hashed password |
| education | TEXT | Education level |
| college | TEXT | College name |
| cgpa | REAL | CGPA (0-10) |
| skills | JSON | Array of skills |
| interests | JSON | Array of interests |
| location_preference | TEXT | Preferred city |
| category | TEXT | Social category |

### Internships
| Field | Type | Description |
|-------|------|-------------|
| id | TEXT (PK) | e.g., INT001 |
| title | TEXT | Internship title |
| organization | TEXT | Hiring organization |
| sector | TEXT | Industry sector |
| location | TEXT | City |
| stipend | INTEGER | Monthly stipend (INR) |
| required_skills | JSON | Required skills array |
| apply_url | TEXT | Application portal URL |
| affirmative_action_required | BOOLEAN | AA flag |

### Matches
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER (PK) | Auto-increment |
| student_id | TEXT (FK) | References students |
| matches | JSON | Ranked match results |
| timestamp | TEXT | Creation timestamp |

## License

This project was developed for **Smart India Hackathon 2025**.
