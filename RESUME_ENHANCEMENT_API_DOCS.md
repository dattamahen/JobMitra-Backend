JobMitra Backend API Documentation - UPDATED
==========================================

Base URL: http://localhost:8000
API Version: v2.0.0

🆕 NEW FEATURE: Resume Enhancement with 3-Agent CrewAI Workflow

==========================================
CORE AI ENDPOINTS
==========================================

1. POST /ask (EXISTING)
   Description: Process user queries using AI agents powered by CrewAI
   Request Body: {"query": "string"}
   Response: {"response": "string", "timestamp": "datetime"}
   Example: POST /ask {"query": "What are Python best practices?"}

🆕 2. POST /resume-enhance (NEW)
   Description: Enhance resumes using 3-agent CrewAI workflow
   Request Body: {
     "resume": "string",
     "job_description": "string"
   }
   Response: {
     "enhanced_resume": "string",
     "timestamp": "datetime"
   }
   Workflow:
   - Agent 1 (Resume Validator): Analyzes resume vs job description
   - Agent 2 (Enhancement Advisor): Suggests specific improvements  
   - Agent 3 (Resume Generator): Creates enhanced final resume
   
   Features:
   ✅ ATS optimization
   ✅ Skill gap analysis
   ✅ Industry-specific customizations
   ✅ Professional formatting improvements
   ✅ Keyword optimization
   ✅ Achievement quantification

3. GET / (EXISTING)
   Description: Health check endpoint for the main application
   Response: {"message": "string", "version": "string", "status": "string", "timestamp": "datetime"}

4. GET /logs (EXISTING)
   Description: Retrieve recent AI query logs
   Query Params: ?limit=10 (max: 100)
   Response: {"logs": "array", "count": "number", "timestamp": "datetime"}

🆕 5. GET /resume-logs (NEW)
   Description: Retrieve recent resume enhancement logs
   Query Params: ?limit=10 (max: 50)
   Response: {
     "resume_logs": [{
       "original_resume": "string",
       "job_description": "string",
       "enhanced_resume": "string", 
       "timestamp": "datetime",
       "process_type": "resume_enhancement"
     }],
     "count": "number",
     "timestamp": "datetime"
   }

==========================================
DATABASE COLLECTIONS
==========================================

📊 query_logs (EXISTING)
- Stores basic query processing interactions
- Fields: query, response, timestamp, user_id

🆕 📊 resume_logs (NEW)
- Stores resume enhancement workflow results
- Fields: original_resume, job_description, enhanced_resume, timestamp, process_type

==========================================
CREWAI AGENT ARCHITECTURE
==========================================

🤖 Agent 1: Resume Validator
- Role: "Resume Validator"
- Goal: Compare resume with job description and return match percentage and gaps
- Expertise: HR professional, ATS specialist, resume screening
- Output: Match analysis, skill gaps, compatibility scores

🤖 Agent 2: Enhancement Advisor  
- Role: "Enhancement Advisor"
- Goal: Suggest updates to the resume based on validation analysis
- Expertise: Resume writer, career coach, optimization strategies
- Output: Actionable improvement recommendations

🤖 Agent 3: Resume Generator
- Role: "Resume Generator"
- Goal: Use suggestions to generate the improved final version
- Expertise: Content writer, formatting expert, ATS optimization
- Output: Enhanced, polished, ATS-ready resume

Sequential Workflow: Agent 1 → Agent 2 → Agent 3
Each agent passes context to the next for comprehensive enhancement.

==========================================
SETUP REQUIREMENTS
==========================================

Environment Variables (.env):
```
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URI=mongodb://localhost:27017/jobmitra
```

Python Dependencies:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
crewai==0.28.8
langchain-openai==0.1.6
motor==3.3.2
pymongo==4.6.0
python-dotenv==1.0.0
pydantic==2.5.0
```

Installation:
```bash
pip install -r requirements.txt
```

==========================================
API EXAMPLES
==========================================

🔹 Basic Query Processing:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What skills are needed for data science?"}'
```

🆕 🔹 Resume Enhancement:
```bash
curl -X POST "http://localhost:8000/resume-enhance" \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "John Doe\nSoftware Developer\nEmail: john@email.com\n\nEXPERIENCE:\nDeveloper at TechCorp (2020-2023)\n- Built web apps\n- Used Python and JS\n\nSKILLS:\nPython, JavaScript, HTML",
    "job_description": "Senior Full Stack Developer\n\nRequirements:\n- 5+ years experience\n- Python, React, Node.js\n- AWS/Azure cloud experience\n- Database knowledge (SQL, MongoDB)\n- DevOps practices"
  }'
```

🔹 Get Resume Enhancement Logs:
```bash
curl -X GET "http://localhost:8000/resume-logs?limit=5"
```

==========================================
TESTING
==========================================

🧪 Run the comprehensive test suite:
```bash
python test_resume_enhancement.py
```

This will test:
✅ Basic CrewAI functionality  
✅ 3-agent resume enhancement workflow
✅ Error handling and validation
✅ Database connectivity

==========================================
ERROR HANDLING
==========================================

🛡️ Comprehensive Error Management:
- Input validation for empty/invalid fields
- Graceful OpenAI API error handling
- Database connection resilience
- User-friendly error messages
- Non-blocking database logging
- Fallback responses for agent failures

==========================================
PRODUCTION CONSIDERATIONS
==========================================

🚀 Before deploying to production:

Security:
- Implement API authentication (JWT tokens)
- Add rate limiting (per user/IP)
- Input sanitization and validation
- HTTPS enforcement

Performance:
- Configure MongoDB indexes
- Implement response caching
- Monitor OpenAI API usage/costs
- Set appropriate timeout values

Monitoring:
- Set up logging levels (INFO/ERROR)
- Track API response times
- Monitor agent workflow completion rates
- Database performance metrics

Scaling:
- Consider agent execution parallelization
- Implement queue system for high-volume requests
- Database connection pooling
- Load balancing for multiple instances

==========================================
CHANGELOG
==========================================

v2.0.0 (Current):
🆕 Added 3-agent resume enhancement workflow
🆕 New /resume-enhance endpoint
🆕 New /resume-logs endpoint  
🆕 Resume enhancement database logging
🆕 Comprehensive error handling
🆕 Test suite for resume enhancement
📝 Updated API documentation

v1.0.0:
- Basic query processing with CrewAI
- MongoDB integration
- Query logging
- Health check endpoint

==========================================

For support or questions about the resume enhancement feature,
check the test_resume_enhancement.py file for implementation examples.
