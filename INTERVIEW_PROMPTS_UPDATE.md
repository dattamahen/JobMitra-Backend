# Interview Prompts Update Documentation

## Overview

Updated the interview prompt system to use a structured template that generates 15-20 questions with progressive difficulty distribution and clear formatting requirements.

## New Prompt Template Structure

### Template Variables
- `{{ROLE}}` - User's job role/position
- `{{SKILLS}}` - Comma-separated list of user's skills  
- `{{TOTAL_EXPERIENCE}}` - User's total years of experience

### Requirements Specification
- **Question Count**: 15-20 questions
- **Progressive Difficulty**: Easy → Medium → Hard
- **Difficulty Distribution**:
  - Easy: 30%
  - Medium: 40% 
  - Hard: 30%
- **Question Types**: Conceptual, practical, and scenario-based
- **No Trick Questions**: Avoid puzzles or gotcha questions

### Output Format
Each question must include:
- Question number (1., 2., 3., etc.)
- Difficulty level in brackets [Easy], [Medium], [Hard]
- Clear, real-world phrasing

### Example Output Format
```
1. [Easy] What is the difference between a list and a tuple in Python?
2. [Medium] How would you implement caching in a REST API?
3. [Hard] Design a scalable microservices architecture for an e-commerce platform.
```

## Updated Files

### 1. `interview_prompts_collection.py`
- Added `get_mock_interview_prompt_template()` function
- Updated sample prompts to use new structured template
- Added difficulty distribution metadata

### 2. `interview_prompts_endpoints.py`
- Updated prompt customization logic
- Implemented proper variable replacement
- Added import for new template function

### 3. `update_interview_prompts.py` (New)
- Database update script for existing prompts
- Creates new prompts if none exist
- Experience-level specific difficulty distributions

### 4. `test_new_interview_prompts.py` (New)
- Comprehensive testing script
- Template format validation
- API endpoint testing with multiple scenarios

## Experience Level Difficulty Adjustments

### Junior (0-1 years)
- Easy: 50%, Medium: 35%, Hard: 15%
- Focus on fundamentals and basic concepts

### Mid-level (1-3 years)  
- Easy: 30%, Medium: 45%, Hard: 25%
- Balanced approach with practical applications

### Senior (3-7 years)
- Easy: 25%, Medium: 40%, Hard: 35%
- More complex scenarios and system design

### Expert (7+ years)
- Easy: 20%, Medium: 35%, Hard: 45%
- Advanced architecture and leadership questions

## Implementation Steps

### 1. Update Database Prompts
```bash
python update_interview_prompts.py
```

### 2. Test New Template
```bash
python test_new_interview_prompts.py
```

### 3. Verify API Endpoints
```bash
# Start server
python main.py

# Test endpoint
curl -X POST "http://localhost:8000/get-interview-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "experience_years": 3,
    "skills": ["Python", "Django", "PostgreSQL"],
    "generate_questions": true
  }'
```

## Benefits of New Structure

1. **Consistent Format**: All questions follow the same numbering and difficulty labeling
2. **Progressive Difficulty**: Questions get harder as the interview progresses
3. **Experience Matching**: Question depth matches candidate's experience level
4. **Real-world Focus**: Practical questions over theoretical puzzles
5. **Clear Requirements**: Specific guidelines for AI generation

## Quality Assurance

### Template Validation
- All template variables must be replaced
- No remaining `{{}}` placeholders
- Proper difficulty distribution
- Question count within 15-20 range

### Question Quality Checks
- Clear, professional phrasing
- Relevant to specified role and skills
- Appropriate difficulty progression
- No trick or puzzle questions
- Real-world applicability

## Future Enhancements

1. **Role-Specific Templates**: Specialized prompts for different job roles
2. **Skill-Based Weighting**: Adjust question focus based on primary skills
3. **Industry Context**: Add industry-specific scenarios
4. **Adaptive Difficulty**: Dynamic adjustment based on previous answers
5. **Multi-language Support**: Templates in different languages

## Troubleshooting

### Common Issues
1. **Template Variables Not Replaced**: Check import and function calls
2. **Wrong Question Count**: Verify AI provider response parsing
3. **Missing Difficulty Labels**: Ensure prompt format requirements are clear
4. **Database Connection**: Verify MongoDB connection in update script

### Debug Commands
```bash
# Check template format
python -c "from interview_prompts_collection import get_mock_interview_prompt_template; print(get_mock_interview_prompt_template())"

# Test variable replacement
python test_new_interview_prompts.py

# Check database prompts
python -c "import asyncio; from db_simple import db; asyncio.run(db.connect()); print('Connected')"
```

## Monitoring and Analytics

Track the following metrics:
- Question generation success rate
- Average question count per session
- Difficulty distribution accuracy
- User satisfaction with question quality
- Interview completion rates

This structured approach ensures consistent, high-quality interview questions that properly assess candidates based on their experience level and target role.