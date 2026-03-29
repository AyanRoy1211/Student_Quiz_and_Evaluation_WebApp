# Student Quiz & Evaluation Web App

A full-stack EdTech web application built with Django that supports three user roles — **Admin**, **Instructor**, and **Student** — with a dual-mode quiz experience: instructors can create quizzes manually or generate them using a RAG-based AI pipeline, and students can attempt assigned quizzes or enter a topic-based AI-powered practice mode.

---

## Tech Stack

**Backend**
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red?style=flat)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT-black?style=flat)

**AI / ML**
![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=flat&logo=google&logoColor=white)
![SentenceTransformers](https://img.shields.io/badge/sentence--transformers-NLP-orange?style=flat)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-blue?style=flat)

**Database & Infrastructure**
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
![dotenv](https://img.shields.io/badge/.env-dotenv-green?style=flat)

**Frontend**
![HTML](https://img.shields.io/badge/HTML5-Templates-E34F26?style=flat&logo=html5&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-CDN-38B2AC?style=flat&logo=tailwind-css&logoColor=white)

---

## Features

### Instructor
- Register and log in as an instructor
- Create quizzes **manually** — add questions and up to 6 choices per question using an inline formset
- Create quizzes **with AI** — enter a topic, difficulty, and optionally upload a PDF; the RAG pipeline generates questions grounded in the uploaded material
- Review, edit, and approve AI-generated questions before publishing
- Publish or unpublish quizzes at any time
- View per-quiz analytics — attempt count, average score, and question-wise accuracy breakdown

### Student
- Register and log in as a student
- **Assigned mode** — browse and attempt quizzes published by instructors, with timed submission
- **Practice mode** — enter any topic and difficulty to get an AI-generated quiz on the fly; results are not saved as formal attempts
- View detailed result breakdown after every attempt — correct answers, selected choices, score, percentage
- Student dashboard showing attempt history, average score, and available quizzes

### Admin
- Admin dashboard with platform-wide statistics: total users, students, instructors, quizzes, and attempts
- Full Django admin panel with inline editing for quizzes, questions, and choices

### REST API
- JWT-authenticated API endpoints for quizzes, attempts, and dashboard data
- Full quiz CRUD for instructors via API
- Submit attempts and retrieve results programmatically
- Token obtain and refresh endpoints

---

## AI Pipeline — RAG-based Quiz Generator

The AI quiz generation feature uses a multi-stage Retrieval Augmented Generation (RAG) pipeline:

1. **Document ingestion** — uploaded PDFs are parsed and split into overlapping chunks using PyMuPDF
2. **Embedding** — each chunk is embedded using `sentence-transformers` (`all-MiniLM-L6-v2`)
3. **Vector search** — chunks are indexed in FAISS; at generation time, the top-k most relevant chunks are retrieved via cosine similarity against the topic query
4. **Prompt construction** — retrieved chunks, topic, difficulty, and output schema are injected into a dynamically built prompt
5. **Generation** — Google Gemini API generates structured JSON containing questions and choices
6. **NLP validation** — pairwise cosine similarity detects duplicate questions; structural checks verify exactly one correct answer per question; failed validations trigger an automatic retry with a corrective prompt
7. **Review** — generated questions land on a review page where the instructor can edit, delete, or approve before saving to the database

---

## Project Structure

```
Student_Quiz_and_Evaluation_WebApp/
│
├── accounts/               # Custom user model, auth views, role decorators
│   ├── models.py           # AbstractUser with role field (admin/instructor/student)
│   ├── views.py            # Register, login, logout, profile, admin dashboard
│   ├── forms.py            # RegisterForm, LoginForm
│   └── decorators.py       # @instructor_required, @student_required, @admin_required
│
├── quizzes/                # Core quiz logic
│   ├── models.py           # Quiz, Question, Choice, Attempt, Response, PracticeAttempt
│   ├── views.py            # All instructor and student views
│   ├── forms.py            # QuizForm, QuestionForm, ChoiceFormSet, GenerateQuizForm
│   └── rag/                # AI pipeline package
│       ├── embedder.py     # sentence-transformers + FAISS index management
│       ├── retriever.py    # PDF chunking and top-k chunk retrieval
│       ├── prompt_builder.py  # Dynamic Gemini prompt construction
│       ├── generator.py    # Gemini API call and JSON parsing
│       └── validator.py    # Duplicate detection and structural validation
│
├── api/                    # Django REST Framework API
│   ├── views.py            # QuizViewSet, AttemptViewSet, submit_attempt, dashboard
│   ├── serializers.py      # All serializers including role-aware ChoiceSerializer
│   ├── permissions.py      # IsInstructor, IsStudent, IsOwnerOrReadOnly
│   └── urls.py             # API routes + JWT token endpoints
│
├── quiz_project/           # Django project settings
│   ├── settings.py         # PostgreSQL, JWT, CORS, dotenv config
│   └── urls.py             # Root URL config with role-based home redirect
│
├── templates/              # HTML templates (Tailwind CSS)
├── static/css/             # Custom animations (custom.css)
├── requirements.txt
├── manage.py
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/token/` | None | Obtain JWT access + refresh tokens |
| POST | `/api/token/refresh/` | None | Refresh access token |
| GET | `/api/quizzes/` | Any | List published quizzes (students) / own quizzes (instructors) |
| POST | `/api/quizzes/` | Instructor | Create a new quiz |
| GET | `/api/quizzes/{id}/` | Any | Retrieve quiz detail with questions |
| PUT/PATCH | `/api/quizzes/{id}/` | Instructor | Update quiz |
| DELETE | `/api/quizzes/{id}/` | Instructor | Delete quiz |
| GET | `/api/attempts/` | Student | List own attempts |
| POST | `/api/submit/` | Student | Submit a quiz attempt |
| GET | `/api/dashboard/` | Student | Student dashboard stats |
| GET | `/api/analytics/{quiz_id}/` | Instructor | Per-quiz analytics with question-wise accuracy |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/AyanRoy1211/Student_Quiz_and_Evaluation_WebApp.git
cd Student_Quiz_and_Evaluation_WebApp
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

```env
SECRET_KEY=your_django_secret_key_here
DEBUG=True
DB_NAME=quiz_db
DB_USER=quiz_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Set up PostgreSQL
```sql
-- Run in psql as postgres superuser
CREATE USER quiz_user WITH PASSWORD 'your_password';
CREATE DATABASE quiz_db OWNER quiz_user;
GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
```

### 6. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser
```bash
python manage.py createsuperuser
```

### 8. Run the development server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` — you will be redirected to the login page.

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | `True` for development, `False` for production | Yes |
| `DB_NAME` | PostgreSQL database name | Yes |
| `DB_USER` | PostgreSQL username | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_HOST` | Database host (default: `localhost`) | Yes |
| `DB_PORT` | Database port (default: `5432`) | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for AI quiz generation | Yes (for AI features) |

---

## User Roles & Access

| Feature | Admin | Instructor | Student |
|---------|-------|-----------|---------|
| Admin dashboard | ✅ | ❌ | ❌ |
| Create quiz (manual) | ❌ | ✅ | ❌ |
| Create quiz (AI) | ❌ | ✅ | ❌ |
| View quiz analytics | ❌ | ✅ (own quizzes) | ❌ |
| Attempt assigned quiz | ❌ | ❌ | ✅ |
| Practice mode (AI) | ❌ | ❌ | ✅ |
| View attempt results | ❌ | ❌ | ✅ (own) |
| Django admin panel | ✅ | ❌ | ❌ |

---

## Roadmap

- [x] Role-based authentication (admin, instructor, student)
- [x] Manual quiz creation with inline choice formsets
- [x] Timed quiz attempts with automatic scoring
- [x] Student and instructor dashboards
- [x] REST API with JWT authentication
- [x] PostgreSQL integration
- [ ] RAG-based AI quiz generator (instructor mode)
- [ ] AI-powered student practice mode
- [ ] NLP validation layer with duplicate detection
- [ ] Student performance insights (weak topic identification)
- [ ] Deployment on Render with managed PostgreSQL

---

## Contributing

This is a personal project built for learning and portfolio purposes. Feel free to fork and extend it.

---

## Author

**Ayan Roy**
B.Tech — Electrical & Electronics Engineering, NIT Sikkim
[GitHub](https://github.com/AyanRoy1211) · [LinkedIn](https://linkedin.com/in/Ayan-Roy) · [Email](mailto:ayanroy0110@gmail.com)