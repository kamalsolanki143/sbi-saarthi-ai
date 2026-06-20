# 🏦 SAARTHI AI
### From Banking Access to Banking Success

> An Agentic AI Banking Companion for SBI Hackathon @ Global Fintech Fest 2026

---

## 🚀 Overview

**SAARTHI AI** is a voice-first, multilingual, multi-agent banking companion designed to improve financial inclusion, digital adoption, and customer engagement for millions of SBI customers.

Instead of forcing users to navigate complex banking applications, SAARTHI acts as an intelligent banking companion that understands customer intent, proactively recommends relevant services, and guides users through banking workflows in natural language.

The platform is especially focused on rural, semi-urban, and first-time digital banking users who often struggle with traditional app-based interfaces.

---

## 🛠️ Completed Backend Features & Hackathon Implementation

The backend of SAARTHI AI has been fully built, tested, and optimized. Here is everything that has been implemented and is ready for review:

1. **Multilingual Voice Integration with Sarvam AI (`sarvam_service.py`)**:
   - Replaced all legacy voice/translation service layers with the state-of-the-art **Sarvam AI** SDK (`Saaras v3` for Speech-to-Text, `Bulbul v3` for Text-to-Speech, and `Mayura` for translation).
   - Real-time voice processing with fallback to compressed text mode or basic text-only mode when bandwidth is low (Graceful Degradation).

2. **Agentic Orchestration & LangGraph Core Workflows (`workflows/`)**:
   - **MARGDARSHAN (Digital Adoption)**: Compiled LangGraph StateGraph that handles customer events, evaluates consent/context, enforces confidence checks, evaluates action constraints, and maps user responses.
   - **Fallback/Clarification Routing (`fallback_graph.py`)**: Seamless redirection when LLM confidence falls below the 85% threshold, prompting the user for clarification before escalating.

3. **Multi-Layer Guardrails & Security Gates (`guardrails/` & `security/`)**:
   - **Consent Validator (DPDP Act Compliance)**: Blocks voice processing, memory storage, and personalized recommendation building unless explicit customer opt-in is granted.
   - **Confidence Checker**: Enforces the 85% confidence floor.
   - **Action Validator**: Hard-blocks unauthorized transaction actions (e.g., loan, SIP, mutual funds recommendations) to comply with hackathon safety boundaries.
   - **Human-in-the-Loop (HIL) Gate**: Prevents the AI from executing any transaction directly. Enforces the strict sequence: `Recommendation Generated` $\rightarrow$ `Action Preview` $\rightarrow$ `MPIN Verification` $\rightarrow$ `Execution`.
   - **MPIN Gate**: Secure verification with lockout rules.

4. **OCR & Document Parsing Engine (`ocr/`)**:
   - Integrated Tesseract OCR to parse Aadhaar and PAN documents, automatically extracting KYC details and identifying qualifying signals for lead generation.

5. **Shared Memory Architecture (`memory/`)**:
   - **Redis Session Memory**: Stores current conversation states and session history, with a thread-safe dict fallback if Redis is unavailable.
   - **ChromaDB Semantic Memory**: Stores vector embeddings of customer interactions to provide contextual history.

6. **Comprehensive 56-Test Suite (`tests/`)**:
   - Verified 100% of routes, security rules, fallback graphs, and service layers. Run with: `pytest tests/ -v`.

---

## 🎯 Problem Statement

Despite having one of the largest banking customer bases in the world, many customers:
- Do not fully utilize digital banking services
- Continue visiting branches for routine activities
- Face language and accessibility barriers
- Struggle with complex banking interfaces
- Miss relevant financial opportunities due to lack of personalization

This leads to low digital adoption, high operational costs, reduced customer engagement, and missed product discovery opportunities.

---

## 💡 Solution

SAARTHI AI introduces an Agentic AI framework that transforms banking from a reactive system into a proactive financial companion.

The system consists of:

### 🧑‍💼 MITRA (Customer Acquisition Agent)
Helps customers discover suitable banking products through natural conversations and guides them through KYC processes.

### 📈 MARGDARSHAN (Digital Adoption Agent)
Guides customers toward the effective use of digital banking services (fixed deposits, UPI, YONO).

### 🤝 SAATHI (Customer Engagement Agent)
Provides proactive financial guidance based on behavioral patterns, spending patterns, and life events.

**All agents are orchestrated through LangGraph workflows and powered by Gemini LLM.**

---

## 🏗️ System Architecture

```text
                    User
                      │
                      ▼
           Voice / Text Interface (Sarvam AI / Speech)
                      │
                      ▼
             Consent Validation (DPDP)
                      │
                      ▼
         Shared Memory (Redis + ChromaDB)
                      │
                      ▼
             Intent detection & Confidence Engine
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       MITRA    MARGDARSHAN    SAATHI
    (Acquisition) (Adoption) (Engagement)
          │           │           │
          └───────────┼───────────┘
                      ▼
               Audit Trail Layer (WebSockets)
                      ▼
             Action Preview Layer
                      │
                      ▼
             Human Verification (MPIN / Biometric Gate)
                      │
                      ▼
             Execution Complete
```

---

## ✨ Safety & Compliance (HIL + DPDP)

### 🛡️ Human-in-the-Loop (HIL) state machine
AI can generate recommendations, but **never executes transactions directly**. Every action is strictly governed by the following sequence:
$$\text{Recommendation Generated} \rightarrow \text{Action Preview} \rightarrow \text{MPIN Verification} \rightarrow \text{Execution}$$
Any bypass attempt raises a safety-critical `HumanInLoopViolationError` (HTTP 403).

### ⚖️ Consent Manager (DPDP Compliance)
Hard-enforces explicit user opt-in before performing any actions:
- **Voice Processing**: Checked before calling speech APIs.
- **Memory Storage**: Checked before writing transaction history/context.
- **Personalized Recommendations**: Checked before recommendations are shown.

### 🔍 Explainable AI (XAI)
Every recommendation object includes a mandatory `why_explanation` field explaining exactly why the customer is receiving the recommendation and which data points were evaluated.

### 🚦 Confidence Fallback Gate
Checks LLM intent confidence. If the score is below the `CONFIDENCE_THRESHOLD` (default: 85%), it stops the recommendation flow, routes to `fallback_graph.py`, and prompts the user with a clarifying question.

---

## 🧰 Tech Stack

* **Web Framework**: FastAPI (Uvicorn)
* **Agentic Orchestration**: LangGraph, LangChain
* **LLM Engine**: Google Gemini (`gemini-1.5-pro`)
* **Voice Layer**: Sarvam AI SDK (`Saaras v3` STT, `Bulbul v3` TTS, `Mayura` Translation)
* **Memory Layer**: Redis (session/state) + ChromaDB (vector semantic interaction logs)
* **OCR engine**: Pytesseract + PIL
* **Validation**: Pydantic v2
* **Persistence**: Flat JSON Database repository (ideal for hackathon demo deployment)

---

## 🚀 Setup & Running Locally

### 1. Prerequisites
- **Python 3.11** (Highly recommended for ChromaDB/Pypika binary compatibility)
- **Tesseract OCR** (Required for document scanning features)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### 2. Installation
Clone the repository, enter the directory, and initialize the virtual environment:
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the template and fill in your API keys:
```bash
cp .env.example .env
```
Ensure you set your `GEMINI_API_KEY` and `SARVAM_API_KEY` in `.env`.

### 4. Run the Dev Server
Start the Uvicorn hot-reloader:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 5. Running Tests
Run the entire backend test suite verifying agents, security, and endpoints:
```bash
pytest tests/ -v
```

---

## 👥 Team Neural Ninjas
- **Kamal Solanki** — Team Lead | AI Architecture & LangGraph Engineering
- **Muskan Yeshmin Ali** — Backend & AI Engineering Lead
- **Sanjana Waghmare** — UI/UX & Product Design Lead
- **Krrish Yaduka** — Frontend Engineering Lead

---

## 📜 License
Developed for the SBI Hackathon @ Global Fintech Fest 2026.
