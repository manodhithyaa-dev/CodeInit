# MindMesh API Contract

## Base URL

```
http://localhost:5000/api
```

## Authentication

All protected endpoints require:

```
Header: Authorization: Bearer <JWT_TOKEN>
```

---

## Auth Routes

### POST /auth/register

Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "string",
  "age_range": "18-24",
  "primary_goal": "MOOD"
}
```

**primary_goal values:** MOOD, MEDICATION, FITNESS, STRESS

**Response (201):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "string",
    "age_range": "18-24",
    "primary_goal": "MOOD",
    "created_at": "2026-02-23T10:00:00"
  }
}
```

---

### POST /auth/login

Login with existing credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { ... }
}
```

**Error (401):**
```json
{
  "detail": "Invalid credentials"
}
```

---

## Journal Routes

### POST /journal

Create journal entry with sentiment analysis.

**Request Body:**
```json
{
  "content": "I am feeling great today and so happy!"
}
```

**Response (201):**
```json
{
  "sentiment_score": 1.0,
  "emotion_label": "Happy",
  "risk_flag": false
}
```

- sentiment_score: -1.0 to 1.0
- risk_flag: true if self-harm/suicide keywords detected

---

### GET /journal

Get all journal entries for authenticated user.

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "content": "I am feeling great today!",
    "sentiment_score": 1.0,
    "emotion_label": "Happy",
    "risk_flag": false,
    "created_at": "2026-02-23T10:00:00"
  }
]
```

---

## Medication Routes

### POST /medications

Add a new medication.

**Request Body:**
```json
{
  "name": "Vitamin D",
  "dosage": "1000IU",
  "frequency_per_day": 1,
  "reminder_time": "09:00:00"
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Vitamin D",
  "dosage": "1000IU",
  "frequency_per_day": 1,
  "reminder_time": "09:00:00"
}
```

---

### GET /medications

List all medications.

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Vitamin D",
    "dosage": "1000IU",
    "frequency_per_day": 1,
    "reminder_time": "09:00:00"
  }
]
```

---

### POST /medications/{medication_id}/taken

Mark medication as taken.

**Request Body:**
```json
{
  "taken_date": "2026-02-23",
  "taken": true
}
```

**Response (200):**
```json
{
  "message": "Updated successfully"
}
```

---

### GET /medications/summary

Get medication adherence summary.

**Response (200):**
```json
{
  "current_streak": 5,
  "weekly_adherence": 85.71
}
```

---

## Fitness Routes

### POST /fitness

Log daily fitness activity.

**Request Body:**
```json
{
  "log_date": "2026-02-23",
  "activity_completed": true,
  "steps": 5000,
  "minutes_exercised": 30,
  "intensity": "MEDIUM"
}
```

**intensity values:** LOW, MEDIUM, HIGH

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "log_date": "2026-02-23",
  "activity_completed": true,
  "steps": 5000,
  "minutes_exercised": 30,
  "intensity": "MEDIUM"
}
```

---

### GET /fitness

Get all fitness logs.

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "log_date": "2026-02-23",
    "activity_completed": true,
    "steps": 5000,
    "minutes_exercised": 30,
    "intensity": "MEDIUM"
  }
]
```

---

### GET /fitness/weekly

Get weekly fitness statistics.

**Response (200):**
```json
{
  "total_steps": 25000,
  "total_minutes": 150,
  "avg_intensity": "MEDIUM",
  "days_active": 5,
  "current_streak": 3
}
```

---

## Support Circle Routes

### POST /circles

Create a new support circle.

**Request Body:**
```json
{
  "name": "My Support Group"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "My Support Group",
  "created_by": 1,
  "created_at": "2026-02-23T10:00:00"
}
```

---

### GET /circles

Get all circles the user is member of.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "My Support Group",
    "created_by": 1,
    "created_at": "2026-02-23T10:00:00"
  }
]
```

---

### POST /circles/{circle_id}/join

Join a support circle.

**Response (200):**
```json
{
  "message": "Joined successfully"
}
```

---

### GET /circles/{circle_id}/members

Get members of a circle.

**Response (200):**
```json
{
  "id": 1,
  "name": "My Support Group",
  "created_by": 1,
  "members": [
    {
      "id": 1,
      "user_id": 1,
      "role": "OWNER"
    },
    {
      "id": 2,
      "user_id": 2,
      "role": "MEMBER"
    }
  ]
}
```

---

### POST /circles/{circle_id}/message

Send encouragement message.

**Request Body:**
```json
{
  "receiver_id": 2,
  "message": "Keep going!"
}
```

**Response (201):**
```json
{
  "id": 1,
  "circle_id": 1,
  "sender_id": 1,
  "receiver_id": 2,
  "message": "Keep going!",
  "created_at": "2026-02-23T10:00:00"
}
```

---

## Insights Routes

### GET /insights/weekly

Get AI-powered weekly insights.

**Response (200):**
```json
{
  "avg_mood": 0.65,
  "fitness_correlation": 0.42,
  "medication_correlation": 0.28,
  "predicted_next_mood": 0.70,
  "summary": "You have been feeling positive lately."
}
```

---

## Error Responses

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized - Invalid credentials |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Testing with curl

### Register:
```bash
curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"123456\",\"name\":\"Test\",\"age_range\":\"18-24\",\"primary_goal\":\"MOOD\"}"
```

### Login:
```bash
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"password\":\"123456\"}"
```

### Journal:
```bash
curl -X POST http://localhost:5000/api/journal -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d "{\"content\":\"I am feeling great!\"}"
```

### Insights:
```bash
curl -X GET http://localhost:5000/api/insights/weekly -H "Authorization: Bearer TOKEN"
```
