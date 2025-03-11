# JOI - Journey of Inner Peace

A mindful meditation app that helps users develop a consistent meditation practice through gamification and social features.

## Features
- Daily personalized meditation instructions
- Streak tracking system
- Achievements and challenges
- Social features and leaderboards
- Timer functionality
- Progress visualization

## Tech Stack
- Backend: Python/Flask
- Frontend: React
- Database: SQLite

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the Flask server:
```bash
python app.py
```

### Frontend Setup
1. Install Node.js and npm if not already installed
2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Run the development server:
```bash
npm run dev
```

## Project Structure
```
joi-meditation/
├── backend/
│   ├── app.py          # Main Flask application
│   ├── models.py       # Database models
│   └── requirements.txt # Python dependencies
└── frontend/
    ├── src/            # React components and styles
    └── package.json    # Node.js dependencies
```
