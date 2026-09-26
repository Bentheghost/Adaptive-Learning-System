<div align="center">

# 🎓 Adaptive E-Learning System
### *AI-Powered Multi-Agent Intelligent Tutoring Platform with Bayesian Knowledge Tracing (BKT)*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

</div>

---

## 📋 Table of Contents
- [Executive Overview](#-executive-overview)
- [Multi-Agent System Architecture](#-multi-agent-system-architecture)
- [Bayesian Knowledge Tracing (BKT) Engine](#-bayesian-knowledge-tracing-bkt-engine)
- [Database Schema & Data Models](#-database-schema--data-models)
- [LLM Service, Caching & Resilience Subsystem](#-llm-service-caching--resilience-subsystem)
- [Gamification Engine](#-gamification-engine)
- [Complete API Reference](#-complete-api-reference)
- [Frontend Architecture & State Management](#-frontend-architecture--state-management)
- [Utility & Administrative Tooling](#-utility--administrative-tooling)
- [Setup & Deployment Guide](#-setup--deployment-guide)

---

## 💡 Executive Overview

The **Adaptive E-Learning System** is an intelligent web application designed to deliver individualized computer science education based on python programming. Powered by **6 autonomous AI agents** built on top of **Google Gemini** and backed by a mathematical **Bayesian Knowledge Tracing (BKT)** engine, the platform continuously tracks learner performance, detects knowledge gaps, adjusts lesson complexity, generates adaptive quizzes, calculates forgetting curves, and provides real-time tutoring.

---

## 🤖 Multi-Agent System Architecture

The core intelligent behavior is divided among 6 specialized AI agents inheriting from an abstract `BaseAgent` class:

```
                ┌────────────────────────┐
                │    CoordinatorAgent    │
                └───────────┬────────────┘
                            │
        ┌───────────┬───────┴───────┬───────────┬───────────┐
        ▼           ▼               ▼           ▼           ▼
  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
  │ Teaching  │ │Assessment │ │ Knowledge │ │Recommend. │ │   Tutor   │
  │   Agent   │ │   Agent   │ │   Agent   │ │   Agent   │ │   Agent   │
  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### 1. Base Agent Framework (`backend/agents/base_agent.py`)
Abstract foundation establishing the cognitive loop:
- **States**: `idle` → `perceiving` → `deciding` → `acting` → `completed` (or `error`).
- **Memory**: Tracks timestamped execution logs for agent telemetry.
- **Methods**: `perceive(environment)`, `decide()`, `act()`.

### 2. Coordinator Agent (`backend/agents/coordinator_agent.py`)
- Central routing brain. Directs incoming tasks (`generate_lesson`, `generate_quiz`, `analyze_knowledge`, `recommend_topic`, `provide_hint`, `chat`) to corresponding agents.
- Collects performance stats, error rates, and success metrics for dashboard monitoring.

### 3. Teaching Agent (`backend/agents/teaching_agent.py`)
- Generates HTML lessons and adaptive review content.
- Evaluates student knowledge levels to choose lesson complexity (`beginner` vs `intermediate`) and example counts.
- Calls `LLMService.generate_lesson_with_prompt()`, returning formatted HTML with key takeaways and code blocks.

### 4. Assessment Agent (`backend/agents/assessment_agent.py`)
- Generates adaptive multiple-choice quizzes (5–7 questions) matching target difficulty (`beginner`, `intermediate`, `advanced`).
- Formats questions, options, correct answers, and step-by-step explanations.

### 5. Knowledge Agent (`backend/agents/knowledge_agent.py`)
- Tracks knowledge evolution, identifies knowledge gaps, and predicts growth.
- Calculates Ebbinghaus forgetting curves ($\text{Priority} = \text{days\_since} \times (1 - \text{level})$) to flag neglected subtopics needing review.
- Triggers database updates via `KnowledgeTracker`.

### 6. Recommendation Agent (`backend/agents/recommendation_agent.py`)
- Optimizes learning paths using a multi-factor scoring algorithm (completion state, prerequisite readiness, difficulty alignment, user goals).
- Selects strategies (`foundation_building` vs `balanced_growth`) and generates step-by-step estimated study time paths.

### 7. Tutor Agent (`backend/agents/tutor_agent.py`)
- Delivers one-on-one assistance, hint generation, conversational AI chat, and motivational feedback.
- Adjusts hint depth (`subtle`, `moderate`, `detailed`) and response style (`guiding`, `explaining`, `showing`) based on student frustration and attempt counts.

---

## 📐 Bayesian Knowledge Tracing (BKT) Engine

Subtopic mastery is tracked in `backend/knowledge_tracker.py` using **Bayesian Knowledge Tracing**:

### BKT Parameters
- $P(L_0) = 0.10$ — Initial prior knowledge probability.
- $P(T) = 0.20$ — Learning transition probability per practice.
- $P(G) = 0.25$ — Guess probability.
- $P(S) = 0.10$ — Slip probability.

### Posterior Updates
- **On Correct Answer ($Obs=1$)**:
  $$P(L_t \mid \text{Correct}) = \frac{P(L_t) \cdot (1 - P(S))}{P(L_t) \cdot (1 - P(S)) + (1 - P(L_t)) \cdot P(G)}$$
  $$P(L_{t+1}) = P(L_t \mid \text{Correct}) + (1 - P(L_t \mid \text{Correct})) \cdot P(T)$$

- **On Incorrect Answer ($Obs=0$)**:
  $$P(L_t \mid \text{Incorrect}) = \frac{P(L_t) \cdot P(S)}{P(L_t) \cdot P(S) + (1 - P(L_t)) \cdot (1 - P(G))}$$
  $$P(L_{t+1}) = P(L_t \mid \text{Incorrect}) + (1 - P(L_t \mid \text{Incorrect})) \cdot P(T)$$

- **Forgetting Curve Decay**:
  $$P(L_{\text{current}}) = P(L_{\text{last}}) \cdot e^{-\lambda \cdot \Delta t} \quad (\lambda = 0.05)$$

---

## 🗄 Database Schema & Data Models (`backend/models.py`)

- `User`: Profile, credentials hash, role (`admin`/`student`), gamification `points`, and `streak_days`.
- `Course`, `Topic`, `Subtopic`: Hierarchical curriculum taxonomy with prerequisites and estimated minutes.
- `UserProgress`: Tracks `knowledge_level` ($0.0 - 1.0$), `confidence`, `quiz_attempts`, `best_score`, `current_phase` ($1$: Lesson, $2$: Quiz, $3$: Mastered), `has_learned`, and `last_accessed`.
- `LearningSession`: Stores generated lesson HTML content and difficulty metadata.
- `QuizAttempt`: Logs quiz scores, question counts, difficulty, and pass status.
- `CachedLesson`, `CachedQuizQuestion`, `CachedExplanation`: Caching tables for ultra-fast LLM responses.
- `ChatMessage`: Conversational history with AI Tutor.
- `TelemetryCache`: Performance key-value store.

---

## ⚡ LLM Service, Caching & Resilience Subsystem (`backend/llm_service.py`)

- **Multi-Tier Caching**: Checks cached lessons ($\pm 0.15$ knowledge tolerance), cached quiz questions, and cached explanation hashes before hitting Gemini API.
- **Exponential Backoff Retry**: Auto-retries requests on `503` or `429` status codes with $2\text{s}, 4\text{s}$ delays.
- **Structured JSON Schema**: Enforces strict JSON schemas for MCQ generation using `types.GenerateContentConfig`.
- **Option Scrambling**: Randomly shuffles MCQ options to prevent position bias.
- **ASCII Safe Logging**: Clean console outputs compatible with all operating systems (Windows CP1252 & UTF-8 terminals).

---

## 🎮 Gamification Engine (`backend/gamification_engine.py`)

- **Lesson Completion**: $+50$ points
- **Quiz Pass ($\ge 70\%$)**: $+100$ points
- **Perfect Quiz ($100\%$)**: $+150$ points
- **Daily Streak Bonus**: $+20 \times \text{streak\_days}$ points
- **Streak Calculation**: Auto-increments on consecutive logins, resets if inactive $>1$ day.

---

## 🔌 Complete API Reference (`backend/app.py`)

| Method | Endpoint | Description | Agent Triggered |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user account | — |
| `POST` | `/api/auth/login` | Authenticate & open session | — |
| `POST` | `/api/auth/logout` | End session | — |
| `GET` | `/api/auth/me` | Fetch active user profile | — |
| `GET` | `/api/courses` | Fetch all courses & user progress | — |
| `GET` | `/api/courses/<id>` | Fetch course details & topics | — |
| `POST` | `/api/learn/lesson` | Generate HTML lesson | **TeachingAgent** |
| `POST` | `/api/learn/quiz` | Generate adaptive quiz questions | **AssessmentAgent** |
| `POST` | `/api/learn/submit-quiz` | Submit quiz & update BKT knowledge | **KnowledgeAgent** |
| `POST` | `/api/learn/explain` | Get AI explanation for question | **TutorAgent** |
| `POST` | `/api/learn/hint` | Get hint for question | **TutorAgent** |
| `GET` | `/api/recommendations` | Get top recommended subtopics | **RecommendationAgent** |
| `GET` | `/api/agent-analytics` | Get real-time AI agent telemetry | **CoordinatorAgent** |
| `POST` | `/api/chat` | AI Tutor Chatbot conversation | **TutorAgent** |

---

## 🎨 Frontend Architecture & State Management (`frontend/src/`)

Built with **React 18**, **Vite**, **Tailwind CSS**, **Framer Motion**, and **Axios**:

```
frontend/src/
├── components/
│   ├── Agent/          # Agent Analytics Monitor (Real-Time Metrics)
│   ├── Auth/           # Login & Registration Components
│   ├── Common/         # Cards, Loaders, Navbar, Footer, GlobalChatbot
│   ├── Dashboard/      # User Dashboard, Progress Gauges, Agent Status
│   ├── Knowledge/      # BKT Mastery Graphs & Forgetting Timelines
│   ├── Learn/          # HTML Lesson Renderer & Live Code Playground
│   ├── Quiz/           # Interactive Quiz Interface & Score Breakdown
│   └── Recommendations/# Learning Path & Recommended Topic Cards
├── context/
│   └── AuthContext.jsx # Global User Auth & Session Context
└── services/
    └── api.js          # Centralized Axios REST API Client
```

---

## 🧰 Utility & Administrative Tooling (`backend/`)

- `seed_quiz.py` / `seed_advanced.py`: Populates default curriculum, topics, subtopics, and quizzes.
- `seed_demo_user.py`: Creates demo student profile with sample progress.
- `reset_progress.py`: Resets user progress for cold-start testing.
- `clear_cache.py`: Flushes all LLM cache tables.
- `delete_users.py` / `list_users.py`: Administrative database user tools.

---

## 🚀 Setup & Deployment Guide

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key ([Get API Key](https://aistudio.google.com/))

### Quick Start (5 Minutes)

1. **Clone Repo**:
   ```bash
   git clone https://github.com/Uzayr-Ch/Adaptive_E-Learning_System.git
   cd Adaptive_E-Learning_System
   ```

2. **Setup Backend**:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate       # Windows
   # source .venv/bin/activate   # macOS / Linux

   pip install -r requirements.txt
   echo GEMINI_API_KEY=your_gemini_api_key > .env
   python seed_quiz.py
   python app.py
   ```
   *Backend running at: `http://localhost:5000`*

3. **Setup Frontend**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   *Frontend running at: `http://localhost:5173`*
