# SQL Conversational Interface

A sophisticated AI-powered conversational interface that answers complex business questions from SQL databases using natural language processing and advanced analytics.

## Project Overview

This application combines React frontend with Python Flask backend to create an intelligent agent capable of handling:
- Complex database schemas
- Bad or unnamed table/column structures  
- Dirty data analysis
- Vague business questions
- Natural language responses with charts and tables

## Architecture

- **Frontend**: React with TypeScript, Chart.js for visualizations
- **Backend**: Python Flask with SQLAlchemy, OpenAI/Claude integration
- **Database**: SQLite for development, PostgreSQL/MySQL support
- **AI**: Large Language Models for query understanding and response generation

## Tech Stack

### Frontend Dependencies
- React 18
- TypeScript
- Axios for API calls
- Chart.js & React-Chartjs-2 for visualizations
- Material-UI for components
- Tailwind CSS for styling

### Backend Dependencies
- Flask with Flask-CORS
- SQLAlchemy for ORM
- OpenAI/Anthropic API clients
- Pandas for data manipulation
- Matplotlib/Plotly for chart generation
- python-dotenv for environment variables

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- OpenAI or Anthropic API key

### Installation

1. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Add your API keys and database configuration

4. **Database Setup**
   ```bash
   cd backend
   python init_db.py
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm start
   ```

The application will be available at `http://localhost:3000`

## Features

- Natural language question processing
- Intelligent SQL query generation
- Dynamic chart and table generation
- Schema analysis and understanding
- Data quality assessment
- Complex analytical capabilities

## Project Structure

```
/
├── frontend/          # React application
├── backend/           # Flask API server
├── database/          # Database files and schemas
├── docs/             # Documentation
└── tests/            # Test files
```