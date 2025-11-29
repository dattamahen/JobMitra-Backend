# Feature Usage Tracking - Backend Implementation

## Overview
Backend implementation for feature usage tracking system with plan-based limits:
- **Free (F)**: 5 features
- **Paid (P)**: 15 features  
- **Pro (S)**: 35 features

## Files Modified/Created

### 1. Database Schema Updates
- **auth_schemas.py**: Added `feature_usage_count` and `feature_usage_status` fields to `UserResponse`
- **auth_db.py**: Added feature usage fields to user creation with default values

### 2. New Endpoints (`feature_usage_endpoints.py`)
- `GET /api/v1/features/usage` - Get current user's feature usage info
- `POST /api/v1/features/use` - Use a paid feature (decrements count)

### 3. Updated Endpoints (`auth_endpoints.py`)
- Login response now includes feature usage data
- `/auth/me` endpoint returns feature usage information

### 4. Application Configuration (`app.py`)
- Added feature usage router to main application

### 5. Migration Script (`migrate_feature_usage.py`)
- Adds feature usage fields to existing users
- Creates feature usage log collection with indexes

## API Endpoints

### GET /api/v1/features/usage
Returns current user's feature usage information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "plan": "F",
  "remaining_count": 3,
  "status": "A"
}
```

### POST /api/v1/features/use
Decrements user's feature count when a paid feature is used.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "feature": "mock_interview"
}
```

**Response:**
```json
{
  "success": true,
  "remaining_count": 2,
  "status": "A",
  "message": "Feature used successfully"
}
```

## Database Schema Changes

### Users Collection
Added fields:
```javascript
{
  "feature_usage_count": 5,        // Number of features remaining
  "feature_usage_status": "A"      // "A" = Available, "X" = eXhausted
}
```

### Feature Usage Log Collection (New)
```javascript
{
  "user_id": "user_123",
  "feature_name": "mock_interview",
  "used_at": "2025-01-27T10:30:00Z",
  "remaining_count": 4,
  "user_plan": "F"
}
```

## Plan Mapping
- `user_plan: "free"` → Plan Code: `"F"` → Limit: 5
- `user_plan: "subscribed"` → Plan Code: `"P"` → Limit: 15
- `user_plan: "pro"` → Plan Code: `"S"` → Limit: 35

## Status Mapping
- `"A"` → User can use paid features (count > 0)
- `"X"` → User has exhausted their feature limit (count = 0)

## Implementation Details

### Feature Usage Flow
1. User attempts to use a paid feature
2. Frontend calls `POST /api/v1/features/use` with feature name
3. Backend checks current count and status
4. If available, decrements count and updates status
5. Logs usage in feature_usage_log collection
6. Returns updated count and status

### Authentication
All feature usage endpoints require valid JWT token in Authorization header.

### Error Handling
- Returns appropriate HTTP status codes
- Provides descriptive error messages
- Handles edge cases (user not found, invalid tokens, etc.)

## Migration Instructions

1. **Run migration script:**
   ```bash
   python migrate_feature_usage.py
   ```

2. **Restart application** to load new endpoints

3. **Verify endpoints** are working:
   ```bash
   # Get feature usage
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/features/usage
   
   # Use a feature
   curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
        -d '{"feature":"mock_interview"}' \
        http://localhost:8000/api/v1/features/use
   ```

## Integration with Frontend

The backend now provides the necessary endpoints for the frontend feature usage service:
- Frontend `FeatureUsageService.getUserFeatureInfo()` calls `GET /api/v1/features/usage`
- Frontend `FeatureUsageService.useFeature()` calls `POST /api/v1/features/use`
- User login/profile endpoints return feature usage data for reactive UI updates

## Security Considerations

1. **Authentication Required**: All endpoints require valid JWT tokens
2. **User Isolation**: Users can only access their own feature usage data
3. **Atomic Operations**: Database updates are atomic to prevent race conditions
4. **Audit Trail**: All feature usage is logged for tracking and analytics

## Testing

Test the implementation with different user plans:
1. Create users with different `user_plan` values
2. Verify correct limits are applied
3. Test feature usage decrements count correctly
4. Verify status changes to "X" when count reaches 0
5. Test error handling for exhausted limits