
# 🧠 MindMesh

AI-Powered Behavioral Health & Habit Reinforcement Platform

MindMesh is a health-tech web platform that integrates **mental health journaling, medication adherence, fitness tracking, and AI-driven behavioral insights** into a unified system.

Built with:

* **Frontend:** React
* **Backend:** FastAPI
* **Database:** MySQL
* **ML Engine:** scikit-learn

---

# 🚀 Core Features

## 1️⃣ Authentication

* User registration
* Secure login
* JWT-based authentication
* Protected API routes

---

## 2️⃣ Smart Journal System

* Daily journal entry submission
* Sentiment scoring
* Emotion classification
* Risk detection (self-harm keyword flagging)
* Mood trend visualization
* Historical journal access

---

## 3️⃣ Medication Tracking

* Add medications
* Set reminder time
* Mark doses as taken
* Track daily streak
* Weekly adherence percentage
* Miss detection logic

---

## 4️⃣ Fitness Tracking

* Log daily activity
* Steps (optional)
* Exercise duration
* Intensity level
* Daily streak tracking
* Weekly summary statistics

---

## 5️⃣ Support Circle

* Create micro support groups
* Invite members
* View member streaks
* Send encouragement messages
* Accountability-based reinforcement

---

## 6️⃣ AI Behavioral Insight Engine

* Weekly mood average
* Mood vs fitness correlation
* Mood vs medication correlation
* Predict next-day mood (Linear Regression)
* AI-generated summary insights

---

# 🧠 AI & ML Components

### Sentiment Engine

* Text classification
* Sentiment score range: `-1.0 → 1.0`
* Emotion labeling
* Risk keyword detection

### Correlation Engine

* Pearson correlation
* Mood vs activity analysis
* Mood vs medication adherence analysis

### Prediction Engine

* Linear Regression
* Predict next-day mood score
* Generate forecast insight

---

# 🏗 Architecture Overview

```
React (Frontend)
        ↓
FastAPI (Backend API)
        ↓
MySQL Database
        ↓
scikit-learn ML Modules
```

---

# 📂 Project Structure

## Backend

```
backend/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── journal.py
│   │   ├── medication.py
│   │   ├── fitness.py
│   │   └── insights.py
│   ├── ml/
│   │   ├── sentiment.py
│   │   ├── correlation.py
│   │   └── prediction.py
```

## Frontend

```
frontend/
│
├── src/
│   ├── pages/
│   ├── components/
│   ├── api/
│   └── App.jsx
```

---

# 🗄 Database Schema (MySQL)

## users

| Field         | Type         | Description                          |
| ------------- | ------------ | ------------------------------------ |
| id            | INT (PK)     | User ID                              |
| email         | VARCHAR(120) | Unique email                         |
| password_hash | VARCHAR(255) | Encrypted password                   |
| name          | VARCHAR(100) | User name                            |
| age_range     | VARCHAR(20)  | Age group                            |
| primary_goal  | ENUM         | MOOD / MEDICATION / FITNESS / STRESS |
| created_at    | TIMESTAMP    | Created time                         |

---

## journal_entries

| Field           | Type         |
| --------------- | ------------ |
| id              | INT (PK)     |
| user_id         | INT (FK)     |
| content         | TEXT         |
| sentiment_score | DECIMAL(4,3) |
| emotion_label   | VARCHAR(50)  |
| risk_flag       | BOOLEAN      |
| created_at      | TIMESTAMP    |

---

## medications

| Field             | Type         |
| ----------------- | ------------ |
| id                | INT (PK)     |
| user_id           | INT (FK)     |
| name              | VARCHAR(100) |
| dosage            | VARCHAR(50)  |
| frequency_per_day | INT          |
| reminder_time     | TIME         |

---

## medication_logs

| Field         | Type     |
| ------------- | -------- |
| id            | INT (PK) |
| medication_id | INT (FK) |
| user_id       | INT (FK) |
| taken_date    | DATE     |
| taken         | BOOLEAN  |

---

## fitness_logs

| Field              | Type                    |
| ------------------ | ----------------------- |
| id                 | INT (PK)                |
| user_id            | INT (FK)                |
| log_date           | DATE                    |
| activity_completed | BOOLEAN                 |
| steps              | INT                     |
| minutes_exercised  | INT                     |
| intensity          | ENUM(LOW, MEDIUM, HIGH) |

---

## support_circles

| Field      | Type         |
| ---------- | ------------ |
| id         | INT (PK)     |
| name       | VARCHAR(100) |
| created_by | INT (FK)     |

---

## circle_members

| Field     | Type                |
| --------- | ------------------- |
| id        | INT (PK)            |
| circle_id | INT (FK)            |
| user_id   | INT (FK)            |
| role      | ENUM(OWNER, MEMBER) |

---

## encouragement_messages

| Field       | Type      |
| ----------- | --------- |
| id          | INT (PK)  |
| circle_id   | INT (FK)  |
| sender_id   | INT (FK)  |
| receiver_id | INT (FK)  |
| message     | TEXT      |
| created_at  | TIMESTAMP |

---

# 🌐 API Contract

Base URL:

```
/api
```

Authentication:

```
Authorization: Bearer <JWT_TOKEN>
```

---

# 🔐 Auth Routes

### POST /api/auth/register

Request:

```json
{
  "email": "user@email.com",
  "password": "123456",
  "name": "User",
  "primary_goal": "MOOD"
}
```

Response:

```json
{
  "token": "jwt_token",
  "user": {}
}
```

---

### POST /api/auth/login

Request:

```json
{
  "email": "user@email.com",
  "password": "123456"
}
```

Response:

```json
{
  "token": "jwt_token",
  "user": {}
}
```

---

# ✍ Journal Routes

### POST /api/journal

Request:

```json
{
  "content": "Feeling low today..."
}
```

Response:

```json
{
  "sentiment_score": -0.45,
  "emotion_label": "Sadness",
  "risk_flag": false
}
```

---

### GET /api/journal

Returns all journal entries for user.

---

# 💊 Medication Routes

### POST /api/medications

Add medication.

### POST /api/medications/{id}/taken

Mark dose as taken.

### GET /api/medications/summary

Returns:

* Current streak
* Weekly adherence %

---

# 🏃 Fitness Routes

### POST /api/fitness

Log activity.

### GET /api/fitness/weekly

Returns weekly stats.

---

# 📊 Insight Routes

### GET /api/insights/weekly

Response:

```json
{
  "avg_mood": 0.12,
  "fitness_correlation": 0.18,
  "medication_correlation": 0.22,
  "predicted_next_mood": 0.15,
  "summary": "On days you exercise, your mood improves by 18%."
}
```

---

# 🧪 Running the Project

## Backend

```
uvicorn app.main:app --reload
```

## Frontend

```
npm install
npm run dev
```

---

# 🎯 Hackathon Focus

MindMesh is not a tracking app.

It is a **behavioral intelligence system** designed to:

* Detect emotional decline
* Reinforce positive habits
* Improve medication adherence
* Predict mood trends

---