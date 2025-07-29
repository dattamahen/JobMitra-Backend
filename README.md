# JobMitra Backend API

A comprehensive REST API built with FastAPI that processes user queries using AI agents powered by CrewAI and OpenAI, with MongoDB integration for complete job search and career development functionality.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **CrewAI Integration**: AI agent-based query processing
- **OpenAI**: GPT-4 powered responses
- **MongoDB**: Async database operations with comprehensive schema
- **User Management**: Complete user profile and authentication system
- **Job Search**: Advanced job search and matching capabilities
- **Application Tracking**: Full job application lifecycle management
- **Mock Interviews**: AI-powered interview practice system
- **Learning Resources**: Skill development and progress tracking
- **Dashboard Analytics**: User activity and progress visualization
- **Environment Configuration**: Secure configuration management

## Project Structure

```
JobMitra-Backend/
├── main.py              # FastAPI application and main endpoints
├── api_routes.py        # Additional API endpoints for all features
├── crew_agent.py        # CrewAI setup and run_crew_ai function
├── db.py               # MongoDB connection and database operations
├── schemas.py          # Pydantic models and MongoDB schema definitions
├── seed_data.py        # Database seeding script with sample data
├── test_api.py         # API testing script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from template)
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Database Schema

The application uses MongoDB with the following collections:

### Collections Overview

1. **user_profiles** - User account and profile information
2. **job_listings** - Job postings and company information
3. **job_applications** - Application tracking and status
4. **resumes** - Resume storage and versioning
5. **mock_interview_sessions** - AI interview practice data
6. **learning_resources** - Skill development materials
7. **skill_assessments** - Assessment results and scores
8. **user_progress** - Learning progress and achievements
9. **user_subscriptions** - Subscription and billing information
10. **user_dashboards** - Dashboard analytics and metrics
11. **query_logs** - AI query and response logging
12. **system_config** - Application configuration settings

### Key Schema Features

- **User Profiles**: Complete professional profiles with skills, preferences, and social links
- **Job Management**: Detailed job listings with requirements, benefits, and HR contacts
- **Application Tracking**: Full application lifecycle with status history
- **Mock Interviews**: AI-powered interview sessions with scoring and feedback
- **Learning System**: Skill-based resources with progress tracking
- **Analytics**: Comprehensive dashboard with user metrics and activity tracking

## Setup Instructions

### 1. Install Dependencies

```bash
cd JobMitra-Backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Update the `.env` file with your actual credentials:

```env
OPENAI_API_KEY=your_actual_openai_api_key
MONGO_URI=mongodb://localhost:27017/jobmitra
```

### 3. MongoDB Setup

Make sure MongoDB is running locally, or update `MONGO_URI` to point to your MongoDB instance.

### 4. Seed Sample Data (Optional)

```bash
python seed_data.py
```

To clear all data:
```bash
python seed_data.py clear
```

### 5. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Core AI Endpoints

#### POST /ask
Process user queries with AI agents.

**Request:**
```json
{
  "query": "What are the best practices for Python web development?"
}
```

**Response:**
```json
{
  "response": "Here are the best practices for Python web development...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### User Management Endpoints

#### POST /api/v1/users
Create a new user profile.

#### GET /api/v1/users/{user_id}
Get user profile by ID.

#### PUT /api/v1/users/{user_id}
Update user profile.

### Job Management Endpoints

#### POST /api/v1/jobs/search
Search for jobs with filters.

**Request:**
```json
{
  "query": "python developer",
  "skills": ["Python", "Django"],
  "location_type": "remote",
  "experience_level": "mid",
  "limit": 20
}
```

#### GET /api/v1/jobs/{job_id}
Get specific job details.

### Application Management Endpoints

#### POST /api/v1/applications
Create a new job application.

#### GET /api/v1/users/{user_id}/applications
Get all applications for a user.

### Mock Interview Endpoints

#### POST /api/v1/mock-interviews
Create a new mock interview session.

#### GET /api/v1/users/{user_id}/mock-interviews
Get mock interview history for a user.

### Dashboard Endpoints

#### GET /api/v1/users/{user_id}/dashboard
Get user dashboard data with analytics.

### Learning Resources Endpoints

#### GET /api/v1/learning-resources
Get learning resources with optional filters.

**Query Parameters:**
- `skill`: Filter by skill (e.g., "Python", "React")
- `level`: Filter by difficulty ("beginner", "intermediate", "advanced")
- `limit`: Number of resources to return

#### GET /api/v1/users/{user_id}/progress
Get user learning progress and achievements.

### System Endpoints

#### GET /
Health check endpoint.

#### GET /logs
Retrieve recent query logs.

#### GET /api/v1/analytics/summary
Get system-wide analytics summary.

#### GET /api/v1/health
Extended health check for all features.

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Database Operations

The database module (`db.py`) provides comprehensive functions for:

- **User Management**: Profile creation, updates, and retrieval
- **Job Operations**: Job search, filtering, and management
- **Application Tracking**: Application lifecycle management
- **Mock Interviews**: Session creation and history tracking
- **Learning Resources**: Skill-based resource management
- **Dashboard Analytics**: User metrics and activity tracking
- **Query Logging**: AI interaction logging and analysis

## Testing

### Running Tests

```bash
python test_api.py
```

### Manual Testing with curl

Test the AI endpoint:
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is FastAPI?"}'
```

Test user creation:
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "email": "test@example.com",
       "full_name": "Test User",
       "skills": ["Python", "FastAPI"]
     }'
```

Test job search:
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "python developer",
       "skills": ["Python"],
       "limit": 5
     }'
```

## Development

### Code Structure

- **main.py**: Core FastAPI application with AI query endpoint
- **api_routes.py**: Extended API endpoints for all features
- **schemas.py**: Pydantic models and MongoDB schema definitions
- **db.py**: Database operations and connection management
- **crew_agent.py**: CrewAI agent configuration and execution
- **seed_data.py**: Database seeding with sample data

### Adding New Features

1. Define Pydantic models in `schemas.py`
2. Add database operations in `db.py`
3. Create API endpoints in `api_routes.py`
4. Update seeding data in `seed_data.py`
5. Add tests in `test_api.py`

### Running in Development Mode

```bash
uvicorn main:app --reload --log-level debug
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `MONGO_URI` | MongoDB connection string | Yes |

## Error Handling

The API includes comprehensive error handling for:

- Input validation and sanitization
- Database connection issues
- AI processing errors
- Authentication and authorization
- Rate limiting and resource constraints
- Graceful fallbacks and error recovery

## Performance Optimizations

- **Database Indexes**: Optimized indexes for fast queries
- **Connection Pooling**: Efficient database connection management
- **Caching**: Strategic caching for frequently accessed data
- **Async Operations**: Non-blocking database and AI operations
- **Query Optimization**: Efficient MongoDB aggregation pipelines

## Production Deployment

For production deployment:

1. Set environment variables securely
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper logging and monitoring
4. Set up database replication and backups
5. Implement authentication and authorization
6. Configure rate limiting and security headers
7. Use a production MongoDB cluster
8. Set up SSL/TLS encryption

## Monitoring and Analytics

The system provides built-in analytics for:

- User engagement and activity tracking
- Job search patterns and preferences
- Application success rates and timelines
- Mock interview performance metrics
- Learning progress and skill development
- API usage and performance monitoring

## License

This project is part of the JobMitra application suite.
