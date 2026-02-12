# Rapidread-summarizer
Rapid Read is an intelligent content summarizer that extracts key insights from YouTube videos, PDFs, web articles, and GitHub repositories. Powered by AI, it transforms lengthy content into concise summaries, saving you hours of reading time.

## Features
- Summarize YouTube videos
- Extract key points from PDFs
- Summarize web articles
- Analyze GitHub repositories
- User authentication and session management
- Save and manage your summaries

## Technology Stack
- Backend: FastAPI (Python)
- Frontend: Streamlit
- Database: MySQL with PyMySQL
- AI: Google Gemini

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Set Up MySQL Database
Follow the instructions in [DATABASE_SETUP.md](DATABASE_SETUP.md) to:
- Install MySQL Server
- Create database and user
- Initialize database tables

### 3. Configure Environment
Make sure your `.env` file has the correct database connection:
```env
DATABASE_URL=mysql+pymysql://rapidread_user:rapidread123@localhost:3306/rapidread_db
GEMINI_API_KEY=your-gemini-api-key
```

### 4. Initialize Database
```bash
python backend/init_database.py
```

### 5. Start the Application

Start the backend:
```bash
python run_backend.py
```

Start the frontend (in a new terminal):
```bash
streamlit run frontend/app.py
```

### 6. Access the Application
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## API Endpoints
- `/auth/register` - Register new user
- `/auth/login` - User login
- `/article/summarize` - Summarize articles
- `/youtube/summarize` - Summarize YouTube videos
- `/pdf/summarize` - Summarize PDF documents
- `/github/summarize` - Summarize GitHub repositories
- `/summaries/` - Get user summaries

## Database Schema
The application uses two main tables:
- `users` - Store user accounts
- `summaries` - Store generated summaries

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for detailed schema information.
