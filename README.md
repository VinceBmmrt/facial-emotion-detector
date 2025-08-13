

# Facial Emotion Scanner
This project uses AI agents to analyze given images and accurately describe the facial expressions detected.
Initially it's just built as an experimental playground for AutoGen designed to explore AutoGen's capabilities with multi-modal inputs, structured outputs, and self-evaluation through an Evaluator Agent.

## 📹 Demo
[Watch the demo here](https://drive.google.com/file/d/1n2accbFPAeryeETTUlTfLFNr9dpnAEDE/view)

## 📂 Project Structure
The project is split into two parts:

### Frontend
- **Framework:** Next.js 15
- **UI:** React 19, Tailwind CSS 4
- **Language:** TypeScript 5

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Dependencies:** Pillow, Pydantic, Uvicorn, Autogen-AgentChat, OpenAI API
- **Features:** Image upload, AI-based facial emotion analysis, structured output parsing, API endpoint for frontend
- **Special Component:** **Evaluator Agent** – validates the quality and consistency of the model’s responses

## 🚀 Features
- Initially a minimal AutoGen integration for multi-modal + structured output testing
- Upload an image and detect:
  - Emotion  
  - Intensity  
  - Estimated age  
- AI-powered analysis via OpenAI models
- Automated validation of outputs using an **Evaluator Agent**
- Fully separated frontend & backend for scalability

## 📦 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/facial-emotion-detector.git
```

### 2. Install dependencies

#### Frontend
from the root folder
```bash
cd frontend
npm install
npm run dev
```

#### Backend
from the root folder
```bash
uv sync ( you need uv from astral )

```

## 🛠 Tech Stack
**Frontend:** Next.js, React, Tailwind CSS, TypeScript  
**Backend:** FastAPI, Python, Pillow, Pydantic, Uvicorn, AutoGen-AgentChat, OpenAI API  
**AI Orchestration:** Multi-agent setup with **Evaluator Agent** for quality control


## Running the Project

from the root folder:
### Backend
Run the backend server with:

```bash
uvicorn backend:app --reload --port 8000
```

This will start the FastAPI server on http://127.0.0.1:8000.

### Frontend
Navigate to the frontend folder and start the Next.js app:
```bash
npm run dev
```
The frontend will be available on http://localhost:3000.
