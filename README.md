# 🏦 SAARTHI AI
### From Banking Access to Banking Success

> An Agentic AI Banking Companion for SBI Hackathon @ Global Fintech Fest 2026

---

## 🚀 Overview

SAARTHI AI is a voice-first, multilingual, multi-agent banking companion designed to improve financial inclusion, digital adoption, and customer engagement for millions of SBI customers.

Instead of forcing users to navigate complex banking applications, SAARTHI acts as an intelligent banking companion that understands customer intent, proactively recommends relevant services, and guides users through banking workflows in natural language.

The platform is especially focused on rural, semi-urban, and first-time digital banking users who often struggle with traditional app-based interfaces.

---

# 🎯 Problem Statement

Despite having one of the largest banking customer bases in the world, many customers:

- Do not fully utilize digital banking services
- Continue visiting branches for routine activities
- Face language and accessibility barriers
- Struggle with complex banking interfaces
- Miss relevant financial opportunities due to lack of personalization

This creates:

- Low digital adoption
- High operational costs
- Reduced customer engagement
- Missed product discovery opportunities

---

# 💡 Solution

SAARTHI AI introduces an Agentic AI framework that transforms banking from a reactive system into a proactive financial companion.

The system consists of:

### 🧑‍💼 MITRA
Customer Acquisition Agent

Helps customers discover suitable banking products through natural conversations.

### 📈 MARGDARSHAN
Digital Adoption Agent

Guides customers toward effective use of digital banking services.

### 🤝 SAATHI
Customer Engagement Agent

Provides proactive financial guidance based on behavioral patterns and life events.

All agents are orchestrated through LangGraph and powered by Gemini.

---

# 🏗️ System Architecture

```text
                    User
                      │
                      ▼
           Voice / Text Interface
                      │
                      ▼
             Consent Validation
                      │
                      ▼
              Shared Memory
                      │
                      ▼
              Intent Detection
                      │
                      ▼
            Confidence Engine
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       MITRA    MARGDARSHAN    SAATHI
          │           │           │
          └───────────┼───────────┘
                      ▼
              Audit Trail Layer
                      ▼
             Action Preview Layer
                      ▼
             Human Verification
            (MPIN / Biometric)
```

---

# ✨ Core Features

## 🎙 Voice-First Banking

- Hindi Support
- Hinglish Support
- Regional Language Ready
- Speech-to-Text
- Text-to-Speech

---

## 🤖 Multi-Agent Architecture

### MITRA

- Smart Onboarding
- Product Discovery
- KYC Assistance
- OCR-Based Document Processing

### MARGDARSHAN

- Salary Credit Detection
- Subsidy Detection
- Idle Balance Detection
- UPI Adoption Guidance
- YONO Adoption Guidance
- Fixed Deposit Recommendations

### SAATHI

- Spending Pattern Analysis
- Life Event Detection
- Education Expense Monitoring
- Festival Spending Insights
- Travel Spending Detection

---

## 🧠 Shared Customer Memory

Maintains:

- Customer Profile
- Language Preference
- Conversation History
- Banking Behavior
- Product Interests
- Agent Interaction History

---

## ⚡ Event-Driven Intelligence

Supported Events:

- Salary Credit
- Subsidy Credit
- Idle Balance Detection
- School Fee Detection
- Festival Spending Detection
- Travel Spending Detection

---

## 🛡️ Security & Compliance

### Human-in-the-Loop

AI can:

✅ Generate Recommendations

AI cannot:

❌ Execute Transactions

Every action requires:

- User Confirmation
- MPIN Verification
- Biometric Authentication

---

### Consent Manager

Explicit consent required for:

- Voice Processing
- Memory Storage
- Personalized Recommendations

---

### Explainable AI

Every recommendation includes:

**Why am I seeing this recommendation?**

---

### Confidence Fallback Logic

If confidence score falls below 85%:

- Agent stops automation
- Clarification request is triggered

---

### Audit Trail

Every decision is recorded:

- Timestamp
- Agent Used
- Confidence Score
- Event Trigger
- Guardrail Status
- Generated Response

---

# 🏛️ Compliance

Built with:

- DPDP Act Principles
- Responsible AI Practices
- Consent-Based Processing
- Data Minimization
- Explainability
- Human Oversight

---

# 🧰 Tech Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Backend

- FastAPI
- Python 3.11+

## AI Layer

- Google Gemini
- LangGraph
- LangChain

## Memory Layer

- Redis
- Vector Memory

## Voice Layer

- Bhashini API

## Validation

- Pydantic

---

# 📂 Project Structure

```text
SAARTHI-AI
│
├── frontend/
├── backend/
├── database/
├── docs/
├── tests/
│
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# 🚦 MVP Scope

The MVP focuses on demonstrating:

### MARGDARSHAN Agent

Workflow:

```text
Salary Credit Event
        ↓
Event Engine
        ↓
Margdarshan Agent
        ↓
FD Recommendation
        ↓
Action Preview
        ↓
MPIN Verification
        ↓
Completion
```

---

# 👥 Team Neural Ninjas

### Kamal Solanki
Team Lead | AI Architecture & LangGraph Engineering

### Muskan Yeshmin Ali
Backend & AI Engineering Lead

### Sanjana Waghmare
UI/UX & Product Design Lead

### Krrish Yaduka
Frontend Engineering Lead

---

# 🎯 Expected Impact

- Improved Digital Adoption
- Reduced Branch Dependency
- Better Financial Inclusion
- Increased Customer Engagement
- Simplified Banking Experience
- Enhanced Accessibility

---

# 🔮 Future Roadmap

- WhatsApp Banking Integration
- SBI YONO Integration
- AI Loan Advisory
- Fraud Detection Agent
- Offline Rural Banking Support
- Family Banking Assistant
- Video KYC Support

---

# 📜 License

This project is developed for the SBI Hackathon @ Global Fintech Fest 2026.

---

## 💙 SAARTHI AI

**From Banking Access to Banking Success**
